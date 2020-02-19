FROM ubuntu:bionic-20190807

MAINTAINER Alexey Nurmukhametov

COPY ./zh /zh

RUN apt-get update && \
    apt-get install -y python python3 python3-pip make gcc nasm git && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y locales && \
# install tools
    pip3 install capstone angr pytest pybind11 && \
    pip3 install psutil && \
    pip3 install \
      ropgadget==v6.0 \
      https://github.com/salls/angrop/archive/794c3f95775b33e854669bb0a3d65b8d6da86f7f.zip \
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
    curl -o z3.tgz -L  https://github.com/Z3Prover/z3/archive/z3-4.6.0.tar.gz && \
    tar zxf z3.tgz && cd z3-z3-4.6.0 && \
    CC=clang CXX=clang++ python scripts/mk_make.py --prefix=/opt/z3 && \
    cd build && make -j4 && make install && cd ../../ && \
    curl -o cap.tgz -L https://github.com/aquynh/capstone/archive/4.0.1.tar.gz && \
    tar xvf cap.tgz && cd capstone-4.0.1/ && ./make.sh && make install && cd ../ && \
    curl -o triton.zip -L https://github.com/JonathanSalwan/Triton/archive/fb3241e94a3e1d0be9831bfc7a865246ee4c9e30.zip && \
    unzip triton.zip && cd Triton* && mkdir build && cd build && \
    cmake ../ -DPYTHON36=on -DZ3_INCLUDE_DIRS=/opt/z3/include -DZ3_LIBRARIES=/opt/z3/lib/libz3.so && make -j4 && make install && \
    cd ../../ && rm -rf capstone-* Triton* cap.tgz triton.zip z3-z3-4.5.0 z3.tgz && \
# install exrop
    pip3 install numba && \
    curl -o exrop.zip -L https://github.com/d4em0n/exrop/archive/c0b39bec2990dd80d5c4ed9a4895fde32817bcfe.zip && \
    unzip exrop.zip && mv exrop-* exrop && rm -rf exrop.zip && \
# install ropium
    curl -o ropium.zip -L https://github.com/Boyan-MILANOV/ropium/archive/f6bb2113474cf39e2aeeb478270bcc235b245301.zip && \
    unzip ropium.zip && mv ropium-* ropium && cd ropium && \
    make -j8 && make install && \
    cd / && rm -rf ropium* && \
# create symlink /bin/sh -> /zh
    rm -rf /bin/sh && ln -s /zh /bin/sh && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# libc.so built with popen calling /bin/bash instead of /bin/sh
COPY ./libc.so /lib/x86_64-linux-gnu/libc.so.6

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
