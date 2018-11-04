#!/bin/bash

source venv/bin/activate
exec hypercorn -b 0.0.0.0:9000 --access-log - --error-log - app:app