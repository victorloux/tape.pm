#!/bin/bash

cd /home/pi/installation/ || echo "File not found"
sudo python3 record.py --startup
