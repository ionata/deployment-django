FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1
ENV ACCEPT_EULA Y

RUN apt-get update -y && apt-get install --auto-remove -y apt-transport-https
RUN apt-get update -y && apt-get install --auto-remove -y \
    software-properties-common \
    apt-utils \
    binutils \
    build-essential \
    curl \
    debconf-utils \
    gettext \
    g++ \
    g++-5\
    gcc \
    gdal-bin \
    git \
    libc-dev \
    libproj-dev \
    locales \
    postgis \
    vim \
  && rm -rf /var/lib/apt/lists/*

# install necessary locales
RUN apt-get install -y locales
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen

# add mssql
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update -y && apt-get install -y msodbcsql unixodbc-dev mssql-tools
RUN ln -s /opt/mssql-tools/bin/* /usr/local/bin/

# add python36
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update -y && apt-get install -y python3.6 python3.6-venv python3.6-dev
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python3
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6 -

# add node8
RUN curl https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
