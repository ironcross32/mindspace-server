#!/bin/sh
clear
rm world.dump*
git pull
python main.py certs/privkey.pem certs/fullchain.pem
