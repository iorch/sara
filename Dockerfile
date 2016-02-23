# SARA
# https://github.com/mxabierto/sara
# Build:
#   docker build -t mxabierto/sara .
# Usage:
# docker run \
#   --name sara \
#   --link sara-mysql:mysql \
#   --link sara-es:elasticsearch \
#   --link sara-redis:redis \
#   -v `pwd`/logs:/logs \
#   -e SARA_MODEL="..." \
#   -e PETITIONS_SERVER_URL="x.x.x.x" \
#   -p 5000:5000 \
#   -d mxabierto/sara

# Base image
FROM mxabierto/jessie

MAINTAINER iorch <j.martinezortega@gmail.com>

# Install dependencies
RUN \
  apt-get update && \
  apt-get install -y \
  python-dev \
  python-pip \
  liblapack-dev \
  libopenblas-dev \
  libxml2-dev \
  python-scipy \
  libmysqlclient-dev \
  libxslt1-dev && \
  ldconfig && \
  rm -rf /var/lib/apt/lists/*

# Add source
ADD requirements.txt /root/sara/requirements.txt
RUN cd /root/sara && \
  pip install --upgrade pip && \
  pip install --force-reinstall --ignore-installed --upgrade -r requirements.txt

ADD . /root/sara/

# Default port
EXPOSE 5000

# Start the classifier service by default
CMD ["/root/sara/start.sh"]
