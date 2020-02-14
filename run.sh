#!/bin/bash

_term() {
  docker stop rop-benchmark > /dev/null
}

trap _term SIGTERM
trap _term SIGINT

docker run --rm -t -v `pwd`:/rop-benchmark/ \
  --name="rop-benchmark" \
  -e PYTHONUNBUFFERED=1 -e PYTHONPATH=/rop-benchmark \
  rop-benchmark \
  bash -c "cd /rop-benchmark && python3 /rop-benchmark/run.py $*" &

child=$!
wait "$child"
