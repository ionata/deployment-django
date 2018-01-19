FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && \
  apt-get install --auto-remove -y \
    apt-transport-https \
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
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    vim \
  && rm -rf /var/lib/apt/lists/*

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql unixodbc-dev

# install SQL Server tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

# install necessary locales
RUN apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen
RUN pip3 install --upgrade pip

# install SQL Server Python SQL Server connector module - pyodbc
RUN pip3 install pyodbc

# Install nodejs 8.x
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
