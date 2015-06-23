#!/bin/bash
cd /root/sara
C_FORCE_ROOT=1 celery -A tasks worker --detach --loglevel=info --logfile="/logs/sara-celery.log"
./ml_classifier.py
