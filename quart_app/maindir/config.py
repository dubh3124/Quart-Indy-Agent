import logging
import os
import asyncio
import json


class Config(object):
    POOL_NAME = os.getenv("POOLNAME")
    POOLGENESIS = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ptgenesis")
    )
    PROTOCOL_VERSION = os.getenv("VERSION")
    AGENTID = json.dumps(
        {"id": os.getenv("AGENTID")}
    )
    AGENTKEY = json.dumps(
        {"key": os.getenv("AGENTKEY")}
    )
    SEED = (
        os.getenv("SEED")
    )
