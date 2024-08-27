#!/usr/bin/env python

"""A utility to monitor internet connectivity.
"""

import argparse
from datetime import datetime, timedelta, tzinfo
from io import TextIOWrapper
import os
from time import sleep
from typing import NoReturn, Optional

from ping3 import ping
from pytz import timezone

# The address to monitor - it's well known
# (it's the primary DNS server for Google DNS)
_ADDR: str = "8.8.8.8"
_POLL_PERIOD_S: int = 10
_FAILURE_RETRY_COUNT: int = 3
_RETRY_POLL_PERIOD_S: int = 1
_OUTPUT_FILE_NAME: str = "out.txt"
_REPORT_FILE_NAME: str = "report.csv"

# Get command parameters
parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="Monitor internet connectivity"
)
parser.add_argument(
    "-t",
    "--timezone",
    help='A recognized timezone, e.g. "Europe/Madrid"'
    " that is used to render printed sates and times."
    " If not provided the system time is used",
)
parser.add_argument(
    "-n",
    "--no-led",
    action="store_true",
    help="Do not use the Power LED to indicate failure."
    " This only has an effect when running on a Raspberry Pi.",
)
args: argparse.Namespace = parser.parse_args()

# Create a timezone object if one was named...
_TZ: Optional[tzinfo] = timezone(args.timezone) if args.timezone else None

# Location of power LED (file)
_RPI_POWER_LED_FILE: str = "/sys/class/leds/PWR/brightness"
# A file that exists only on a Raspberry Pi
# that contains the model name.
_RPI_FILE: str = "/sys/firmware/devicetree/base/model"

# Are we on a Raspberry PI?
# Try to read the model file.
_IS_RPI: bool = False
try:
    with open(_RPI_FILE, "r", encoding="utf-8") as model_file:
        if "raspberry pi" in model_file.read().lower():
            _IS_RPI = True
except FileNotFoundError:
    pass


def power_led_on() -> None:
    """Used to switch on the bright RED power LED
    (to indicate connection failure on a Raspberry Pi)
    """
    if _IS_RPI:
        _ = os.system(f"echo 1 | sudo tee {_RPI_POWER_LED_FILE} > /dev/null")


def power_led_off() -> None:
    """Used to switch the bright RED power LED off
    (to indicate success)
    """
    if _IS_RPI:
        _ = os.system(f"echo 0 | sudo tee {_RPI_POWER_LED_FILE} > /dev/null")


def main(output: TextIOWrapper, report: TextIOWrapper) -> NoReturn:
    """Main loop."""
    failure_start: Optional[datetime] = None
    failure_retry_start: Optional[datetime] = None
    success_start: Optional[datetime] = None
    # On first failure, how often have we retried?
    # When this reaches _FAILURE_RETRY_COUNT then it'a a failure.
    failure_retry_count: int = 0

    # Always start with LED on.
    # This switches the LED on even if the user has asked not to control the LED.
    # i.e. it sets the RPi's default state.
    power_led_on()

    output.write("----------\n")
    output.write("Monitoring\n")
    output.write(f'Connection to "{_ADDR}" (timezone={_TZ})...\n')
    output.flush()

    report_start_time: Optional[str] = None
    while True:
        # Ping the remote server...
        time_now: datetime = datetime.now(_TZ).replace(microsecond=0)
        response = ping(_ADDR)
        # Typical ping wait.
        # During retry this may be shorter.
        sleep_period_s: int = _POLL_PERIOD_S

        # Success?
        if isinstance(response, float):
            # Got a successful 'ping'
            # - always reset the failure retry count
            failure_retry_count = 0
            # Start of a new success sequence?
            if not success_start:
                # And this is the first success
                # (in a potential sequence)
                if not args.no_led:
                    # Extinguish the power LED
                    # (indicates success)
                    power_led_off()
                # And this is the first success in sequence...
                msg: str = f"Connection success at {time_now}"
                # Have we just emerged from a failure?
                if failure_start:
                    down_time: timedelta = time_now - failure_start
                    output.write(f"{msg} [+] down for {down_time}\n")
                    failure_start = None
                    if report_start_time:
                        # Commit the failure to the report file.
                        # Each line consists of the start of the failure
                        # and the duration of the failure.
                        report.write(f"{report_start_time},{down_time}\n")
                        report.flush()
                        report_start_time = None
                else:
                    output.write(f"{msg}\n")
                output.flush()
                success_start = time_now
                failure_retry_start = None
        else:
            # 'ping' failed
            if not failure_start:
                # And this is the first failure
                # (in a potential sequence)

                # Exhausted retry count?
                if failure_retry_count < _FAILURE_RETRY_COUNT:
                    if failure_retry_count == 0:
                        # First failure
                        failure_retry_start = time_now
                    # Count this failure,
                    # and shorten the poll period (during retry attempts)
                    failure_retry_count += 1
                    sleep_period_s = _RETRY_POLL_PERIOD_S
                    output.write(
                        f"Connection failure at {time_now}"
                        f" (retry {failure_retry_count}/{_FAILURE_RETRY_COUNT})\n"
                    )
                else:
                    if not args.no_led:
                        # Firstly - illuminate the power LED on
                        # (to indicate failure)...
                        power_led_on()
                    # Record the time of this failure,
                    # preventing us re-entering this block until another success.
                    failure_start = (
                        failure_retry_start if failure_retry_start else time_now
                    )
                    # And the first time in succession
                    msg = f"Connection failure at {failure_start}"
                    # How long has the connection been up?
                    up_time: Optional[timedelta] = None
                    if success_start:
                        up_time = time_now - success_start
                        success_start = None
                    if up_time:
                        output.write(f"{msg} [-]   up for {up_time}\n")
                        report_start_time = failure_start.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        output.write(f"{msg}\n")
                output.flush()

        # Pause
        sleep(sleep_period_s)


if __name__ == "__main__":
    with open(_OUTPUT_FILE_NAME, "a", encoding="utf-8") as output_file, open(
        _REPORT_FILE_NAME, "a", encoding="utf-8"
    ) as report_file:
        main(output_file, report_file)
