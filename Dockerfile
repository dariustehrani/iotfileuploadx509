FROM ubuntu:20.04
LABEL Name=azure-iot-python 
LABEL Version=0.0.1

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

CMD [ "/bin/bash" ]

# update os & install some basic packages needed later
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y -qq \
    && apt-get upgrade -y -qq \
    && apt-get install -y -qq --no-install-recommends \
    wget gnupg curl bzip2 ca-certificates apt-transport-https unzip perl openssl

# setup python3
RUN apt-get update && apt-get install -y -qq --no-install-recommends \
    python3 python3-dev python3-pip python-is-python3

RUN apt-get autoremove -y -qq \
    && apt-get clean -qq \
    && rm -rf /var/lib/apt/lists/*

RUN python --version
# RUN echo "alias pip='/usr/bin/pip3'" >> /etc/environment

RUN pip3 install azure-iot-device azure.storage.blob

RUN mkdir /pythoniot
RUN chmod 777 /pythoniot
COPY ./code/* /pythoniot/
