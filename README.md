# MoNet

[![lint](https://github.com/alanbchristie/monet/actions/workflows/lint.yaml/badge.svg)](https://github.com/alanbchristie/monet/actions/workflows/lint.yaml)

![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/alanbchristie/monet)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MOnitor NETwork - a Python utility to monitor internet connectivity.
Written to test broadband connections. The utility
tries to `ping` a well-known IP address (`8.8.8.8`) every 10 seconds
and reports when the connection is available, and when it is not.

A typical output will look something like the following: -

    Monitoring network connection to "8.8.8.8" (timezone=Europe/Madrid)...
    Connection success at 2023-09-03 19:11:35+02:00
    Connection failure at 2023-09-04 11:23:03+02:00 (retry 1/3)
    Connection failure at 2023-09-05 02:27:54+02:00 (retry 1/3)
    Connection failure at 2023-09-05 02:27:59+02:00 (retry 2/3)
    Connection failure at 2023-09-05 02:28:04+02:00 (retry 3/3)
    Connection failure at 2023-09-05 02:27:54+02:00 [-]   up for 1 day, 7:16:34
    Connection success at 2023-09-05 02:28:24+02:00 [+] down for 0:00:30
    Connection failure at 2023-09-05 09:40:13+02:00 (retry 1/3)

In the above output the program is started at 19:11:35 on the 3rd of September.
There is a short outage at 11:23:03 on the 4th September, which recovers,
followed by a prolonged one that starts at 02:27:54 on the 5th, recovering at 02:28:24.

# Usage
Form a virtual environment: -

    pip install -r requirements.txt
    python monet.py

Or, for background monitoring you can use `nohup` and watch `out.txt`
to observe progress: -

    nohup python -u ./monet.py -t Europe/Madrid &

>   When run on an RPi this code uses the [Power LED] to indicate failure,
    unless `--no-led` is specified (see `monet.py -h`).

## Installation
You typically run `monet` as a systemd service on a Raspberry Pi.
The repository contains an example service file that you can use as a template.

Clone the repository to your Pi, create an environment and install the
requirements, and install the service file: -

    git clone https://github.com/alanbchristie/monet
    cd monet
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Edit the `monet.service` file to match your needs and then install it: -

    sudo cp monet.service /lib/systemd/system
    sudo chmod 644 /lib/systemd/system/monet.service
    sudo systemctl daemon-reload
    sudo systemctl enable monet.service
    sudo systemctl start monet

And then reboot the Pi to make sure the service starts automatically on boot.

    sudo reboot

---

[power led]: https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
