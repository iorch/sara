# SARA
# https://github.com/mxabierto/sara
# Build:
#   docker build -t mxabierto/sara .
# Usage:
#   docker run --rm \
#     --name sara \
#     --link sara-mysql:mysql \
#     --link sara-es:elasticsearch \
#     -p 5000:5000 -d mxabierto/sara

# Base image
FROM mxabierto/base

MAINTAINER bcessa <ben@pixative.com>

# Install dependencies
RUN \
  apt-get update && \
  apt-get install -y \
  gcc \
  g++ \
  gfortran \
  git-core \
  liblapack-dev \
  libmysqlclient-dev \
  libopenblas-dev \
  libxml2-dev \
  libxslt1-dev \
  python-dev \
  python-pip && \
  rm -rf /var/lib/apt/lists/*

# Add source
ADD . /root/sara

# App setup
RUN \
  mkdir /root/sara/{data,plots,models} && \
  pip install -r /root/sara/requirements.txt && \
  chmod 775 /root/sara/ml_classifier.py

# Default port
EXPOSE 5000

# Start the classifier service by default
CMD ["/root/sara/ml_classifier.py"]