import logging
import os
import asyncio
import json
from quart_app.indyutils.agent import Agent


class Config(object):
    POOL_NAME = "pool201"
    POOLGENESIS = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ptgenesis")
    )
    PROTOCOL_VERSION = 2
    MAINAGENTID = json.dumps({"id": "Agent"})
    MAINAGENTCREDS = json.dumps({"key": "SuperAgent!"})




