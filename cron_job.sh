#!/bin/bash
cd /home/thunder/workspace/exercise00 && ./geqdata.py -u | while IFS= read -r line; do echo "$(date) $line";done | tee logfile.txt
