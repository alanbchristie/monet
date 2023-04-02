# MoNet

[![lint](https://github.com/alanbchristie/monet/actions/workflows/lint.yaml/badge.svg)](https://github.com/alanbchristie/monet/actions/workflows/lint.yaml)

MOnitor NETwork - a Python utility to monitor internet connectivity.
Written to test broadband connections. The utility
tries to `ping` a well-known IP address (`8.8.8.8`) every 10 seconds
and reports when the connection is available, and when it is not.

Form a virtual environment: -

    pip install -r requirements.txt
    python monet.py

Or, for background monitopring you can use `nohup`: -

    nohup python -u ./monet.py -t Europe/Madrid &

>   When run on an RPi this code uses the [Power LED] to indicate failure,
    unless `--no-led` is specified (see `monet.py -h`).

---

[power led]: https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
