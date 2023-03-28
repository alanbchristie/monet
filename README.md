# MoNet
MOnitor NETwork - a Python utility to monitor internet connectivity.
Written to test broadband connections. The utility
tries to `ping` a well-known IP address (`8.8.8.8`) every 10 seconds
and reports when the connection is available, and when it is not.

Form a virtual environment: -

    pip install -r requirements.txt
    python monet.py
