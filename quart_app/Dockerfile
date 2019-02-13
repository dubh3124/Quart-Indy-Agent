FROM rcarmo/ubuntu-python:3.7-amd64

ARG uid=1000
ARG indy_stream=stable

ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"
ENV SHELL="/bin/bash"

# Create a user
RUN useradd -d /home/quart -ms /bin/bash -G sudo -p quart quart
# Set working directory for the purpose of this Dockerfile
WORKDIR /home/quart

RUN apt-get update -y && apt-get install -y \
    wget \
    python-setuptools \
    python3-nacl \
    apt-transport-https \
    ca-certificates \
    build-essential \
    pkg-config \
    cmake \
    libssl-dev \
    libsqlite3-dev \
    libsodium-dev \
    curl

# Install LibIndy
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial $indy_stream" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y libindy


# Copy requirements to the app root
COPY quart_app/requirements.txt ./
# Create a virtual environment and install the dependecies
RUN python -m venv venv && \
  venv/bin/pip install --no-cache-dir -r requirements.txt --upgrade && \
  chown -R quart:quart ./

# Copy the app into our user root
COPY quart_app/ /home/quart
# Make our entrypoint executable
RUN chmod +x boot.sh

# Set the user
USER quart
# Set the entrypoint
ENTRYPOINT ["bash", "./boot.sh"]