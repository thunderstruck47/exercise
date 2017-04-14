#!/bin/bash
cd /home/thunder/Projects/exercise && ./update.py | while IFS= read -r line; do echo "$(date) $line";done | tee logfile.txt
