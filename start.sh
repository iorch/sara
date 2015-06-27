#!/bin/bash
cd /root/sara
wget ${SARA_MODEL}
tar xzf sara-model-0.1.tgz
C_FORCE_ROOT=1 celery -A tasks worker --detach --loglevel=info --logfile="/logs/sara-celery.log"
./ml_classifier.py
