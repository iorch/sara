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
FROM mxabierto/python

MAINTAINER bcessa <ben@pixative.com>

# Install dependencies
RUN \
  apt-get update && \
  apt-get install -y \
  liblapack-dev \
  libopenblas-dev \
  libxml2-dev \
  libxslt1-dev && \
  ldconfig && \
  rm -rf /var/lib/apt/lists/*

# Add source
ADD . /root/sara

# Default port
EXPOSE 5000

# Start the classifier service by default
CMD ["/root/sara/start.sh"]