#!/usr/bin/env python
#
# Used to monitor internet connectivity.
# Run from a virtual environment with something like
# this to get the activity in "nohup.out": -
#
#   $ nohup python -u ./monet.py -t Europe/Madrid &

import argparse
from datetime import datetime, timedelta
from time import sleep
from typing import Optional

from ping3 import ping
from pytz import timezone

# The address to monitor - it's well known
# (it's the primary DNS server for Google DNS)
_ADDR: str = '8.8.8.8'
_POLL_PERIOD_S: int = 10

# Get command parameters
parser: argparse.ArgumentParser =\
    argparse.ArgumentParser(description='Monitor internet connectivity')
parser.add_argument('-t', '--timezone',
                    help='A recognized timezone, e.g. "Europe/Madrid"'
                         ' that is used to render printed sates and times.'
                         ' If not provided the system time is used')
args: argparse.Namespace = parser.parse_args()

# Create a timezone object if one was named...
_TZ: Optional[timezone] = timezone(args.timezone) if args.timezone else None

_FAILURE_START: Optional[datetime] = None
_SUCCESS_START: Optional[datetime] = None

print(f'Monitoring network connection to "{_ADDR}" (timezone={_TZ})...')
while True:
    # Ping the remote server...
    time_now: datetime = datetime.now(_TZ).replace(microsecond=0)
    response = ping(_ADDR)
    
    # Success?
    if isinstance(response, float):
        # Got a successful 'ping'
        if not _SUCCESS_START:
            # And this is the first success in sequence... 
            msg: str = f'Connection success at {time_now}'
            # Have we just emerged from a failure?
            if _FAILURE_START:
                down_time: timedelta = time_now - _FAILURE_START
                print(f'{msg} [+] down for {down_time}')
                _FAILURE_START = None
            else:
                print(msg)
            _SUCCESS_START = time_now
    else:
        # 'ping' failed
        if not _FAILURE_START:
            # And the first time in succession
            msg = f'Connection failure at {_FAILURE_START}'
            # How long has the connection been up?
            up_time: Optional[timedelta] = None
            if _SUCCESS_START:
                up_time = time_now - _SUCCESS_START
            # Record the time of this failure,
            # preventing us-reentering this block until after another success...
            _FAILURE_START = time_now
            if up_time:
                print(f'{msg} [-] up for {up_time}')
            else:
                print(msg)
                
    # Pause
    sleep(_POLL_PERIOD_S)
