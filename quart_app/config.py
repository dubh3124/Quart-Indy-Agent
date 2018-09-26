import logging
import os
import asyncio

class Config(object):
    POOL_NAME = "pool20"
    POOLGENESIS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ptgenesis'))
    PROTOCOL_VERSION = 2
