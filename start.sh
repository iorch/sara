#!/bin/bash
# Download compiled dependencies bundle
tempdir=$(mktemp -d /tmp/wheel-XXXXX)
cd $tempdir
wget https://s3.amazonaws.com/org.mxabierto/sara/deps.tbz2
tar xjf deps.tbz2
rm deps.tbz2

# Download trained model
cd /root/sara
wget ${SARA_MODEL}

# Unpack model and install dependencies
tar xzf model-0.1.tgz
pip install --force-reinstall --ignore-installed --upgrade --no-index --no-deps $tempdir/*

# Start application
C_FORCE_ROOT=1 celery -A tasks worker --detach --loglevel=info --logfile="/logs/sara-celery.log"
./ml_classifier.py
