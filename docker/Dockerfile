FROM ubuntu:bionic-20190807 

MAINTAINER Alexey Nurmukhametov

COPY ./zh /zh

RUN apt-get update && \
    apt-get install -y python python3 python3-pip make gcc nasm git && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y locales && \
    pip3 install capstone ropgadget angr pytest pybind11 && \
    pip3 install \
      https://github.com/salls/angrop/archive/794583f59282f45505a734b21b30b982fceee68b.zip \
      https://github.com/programa-stic/barf-project/archive/4a003e72f1dbee2723b9ece8b482473531145e8e.zip \
      https://github.com/Boyan-MILANOV/ropgenerator/archive/c63c81f03e8653dc3911e21300c00003a4224f6a.zip \
      https://github.com/sashs/Ropper/archive/781adfa0859637d653a5c0f6b17a7eff2560787f.zip && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    sed 's@#!/bin/sh@#!/bin/bash@g' -i /sbin/ldconfig && \
    rm /bin/sh && ln -s /zh /bin/sh && \
    rm -rf /var/lib/apt/lists/* /root/.cache

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8     
