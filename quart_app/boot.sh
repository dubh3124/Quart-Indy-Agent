#!/bin/bash

cd /home/quart
python -m venv venv && \
  venv/bin/pip install --no-cache-dir -r requirements.txt --upgrade && \
  chown -R quart:quart ./
source ./venv/bin/activate
exec hypercorn -b 0.0.0.0:9000 --access-log - --error-log - app:app