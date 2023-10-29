#!/bin/bash

# Get the current directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Generate the service file dynamically
echo "[Unit]
Description=Tado Auto-Assist Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $DIR/tado_aa.py
Restart=always
User=$USER
Group=$USER
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=tado_aa

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/tado_aa.service > /dev/null

# Reload systemd to recognize the service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable tado_aa.service

# Start the service
sudo systemctl start tado_aa.service

echo "Installation complete!"