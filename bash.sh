#!/bin/bash

docker run --rm -it -v `pwd`:/rop-benchmark/ \
  -e PYTHONUNBUFFERED=1 -e PYTHONPATH=/rop-benchmark \
  rop-benchmark /bin/bash
