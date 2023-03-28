#!/usr/bin/env python
#
# Used to monitor internet connectivity.
# Run from a virtual environment with something like
# this to get the activity in "nohup.out": -
#
#   $ nohup python -u ./monet.py &

from datetime import datetime, timedelta
from time import sleep
from typing import Optional

from ping3 import ping
from pytz import timezone

_ADDR: str = '8.8.8.8'
_TIMEZONE: str = 'Europe/Madrid'

_FIRST_ITERATION: bool = True
_FAIL_START: Optional[datetime] = None
_OK_START: Optional[datetime] = None
_POLL_PERIOD_S: int = 10

_TZ: timezone = timezone(_TIMEZONE)

print(f'Monitoring network connection to "{_ADDR}" (timezone={_TZ})...')
while True:
    response = ping(_ADDR)
    time_now: datetime = datetime.now(_TZ).replace(microsecond=0)
    if isinstance(response, float):
        if _FAIL_START:
            down_time: timedelta = time_now - _FAIL_START
            print(f'Connection restored at {time_now} [-] {down_time}')
            _FAIL_START = None
        elif _FIRST_ITERATION:
            print(f'Connection is OK at {time_now}')
        _OK_START = time_now
    elif not _FAIL_START:
        up_time: Optional[timedelta] = None
        if _OK_START:
            up_time = time_now - _OK_START
        _FAIL_START = time_now
        if up_time:
            print(f'Connection failed at {_FAIL_START} [+] {up_time}')
        else:
            print(f'Connection failed at {_FAIL_START}')
    _FIRST_ITERATION = False
    sleep(_POLL_PERIOD_S)
