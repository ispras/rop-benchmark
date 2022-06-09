FROM ubuntu:20.04

MAINTAINER Alexey Nurmukhametov

ARG DEBIAN_FRONTEND=noninteractive

COPY ./zh /zh

RUN apt-get update && \
    apt-get install -y python python3 python3-pip make gcc nasm git && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y locales && \
# install tools
    pip3 install capstone angr pytest pybind11 && \
    pip3 install psutil && \
    pip3 install \
      ropgadget==v6.3 \
      https://github.com/salls/angrop/archive/794583f59282f45505a734b21b30b982fceee68b.zip \
      https://github.com/programa-stic/barf-project/archive/4a003e72f1dbee2723b9ece8b482473531145e8e.zip \
      https://github.com/Boyan-MILANOV/ropgenerator/archive/c63c81f03e8653dc3911e21300c00003a4224f6a.zip \
      https://github.com/sashs/Ropper/archive/75a9504683427e373c7bb6d6a54ed20bd98905ff.zip && \
# uncomment locales and generate them
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen && \
# replace some shebangs to /bin/bash
    sed 's@#!/bin/sh@#!/bin/bash@g' -i /sbin/ldconfig && \
    sed 's@#!/bin/sh@#!/bin/bash@g' -i /bin/lesspipe && \
# install triton
    apt-get install -y curl unzip cmake libboost-dev nano && \
    pip3 install pwn && \
    curl -o z3.tgz -L https://github.com/Z3Prover/z3/archive/refs/tags/z3-4.8.17.tar.gz && \
    tar zxf z3.tgz && cd z3-z3-4.8.17 && \
    CC=clang CXX=clang++ python scripts/mk_make.py --prefix=/opt/z3 && \
    cd build && make -j$(nproc) && make install && cd ../../ && \
    curl -o cap.tgz -L https://github.com/aquynh/capstone/archive/4.0.1.tar.gz && \
    tar xvf cap.tgz && cd capstone-4.0.1/ && ./make.sh && make install && cd ../ && \
    curl -o triton.zip -L https://github.com/JonathanSalwan/Triton/archive/fb3241e94a3e1d0be9831bfc7a865246ee4c9e30.zip && \
    unzip triton.zip && cd Triton* && mkdir build && cd build && \
    cmake ../ -DPYTHON36=on -DZ3_INCLUDE_DIRS=/opt/z3/include -DZ3_LIBRARIES=/opt/z3/lib/libz3.so && make -j$(nproc) && make install && \
    cd ../../ && rm -rf capstone-* Triton* cap.tgz triton.zip z3-z3-* z3.tgz && \
# install exrop
    curl -o exrop.zip -L https://github.com/d4em0n/exrop/archive/343eee05bd4b9d31db3e55a70a33893527225c84.zip && \
    unzip exrop.zip && mv exrop-* exrop && rm -rf exrop.zip && \
# install ropium
    curl -o ropium.zip -L https://github.com/Boyan-MILANOV/ropium/archive/e7100878b75e55d775eecfd79bd549f9895f4c8c.zip && \
    unzip ropium.zip && mv ropium-* ropium && cd ropium && \
    make -j$(nproc) && make install && \
    cd / && rm -rf ropium* && \
# create symlink /bin/sh -> /zh
    rm -rf /bin/sh && ln -s /zh /bin/sh && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# libc.so built with popen calling /bin/bash instead of /bin/sh
COPY ./libc.so /lib/x86_64-linux-gnu/libc.so.6

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
