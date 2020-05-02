#!/bin/sh
./stop.sh
python3 filelink.py >> log.txt 2>&1 & echo $! >> log.pid
