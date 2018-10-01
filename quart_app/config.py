import logging
import os
import asyncio
import json


class Config(object):
    POOL_NAME = "pool20"
    POOLGENESIS = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ptgenesis")
    )
    PROTOCOL_VERSION = 2
    AGENT1ID = "Herman"
    AGENT1CREDS = "Green3124!"
    AGENT2ID = json.dumps({"id": "Jane"})
    AGENT2CREDS = json.dumps({"key": "Green3124!"})
