# tado_aa (Tado Auto-Assist for Geofencing and Open Window Detection + Temperature limit)

A python script that automatically adjusts the temperature in your home upon leaving or arriving based on your settings from the tado app. It also automatically switches off the heating (activating Open Window Mode) in the room where the tado TRV detects an open window.
In addition, it offers the possibility to configure the minimum and maximum temperature allowed.

## Prerequisites

- Python 3
- PyTado: This script relies on PyTado. Install it using:
  `pip3 install python-tado`

This script was made possible because of PyTado's author, Chris Jewell (chrism0dwk@gmail.com), and the person who modified it, Wolfgang Malgadey (wolfgang@malgadey.de).

## Installation

To install and start the Tado Auto-Assist Service, follow these steps:

1. Clone the repository using `git` (to check if it's installed run `sudo apt install git`, in case it isn't it will ask if you want to install it, press `y` to confirm):
   - `git clone https://github.com/adrianslabu/tado_aa`

2. Navigate to the cloned directory:
   - `cd tado_aa`

3. Edit `tado_aa.py` using a text editor, in this exemple I will use `nano` (to check if it's installed run `sudo apt install nano`, in case it isn't it will ask if you want to install it, press `y` to confirm.):
   - `nano tado_aa.py`
   - use arrows to navigate to the desired line and change `username` and `password` with your Tado username and password
   - press `Ctrl` + `x` simultaneously, don't change the file name, now just press `enter` to save it

4. Run the installation script (in case of error run `sudo chmod +x install.sh` and retry):
   - `./install.sh`

This will set up the service to run automatically and start it immediately.

## If you want to thank me

[Paypal](https://paypal.me/adrianslabu) /
[Buymeacoffee](https://www.buymeacoffee.com/adrianslabu)
