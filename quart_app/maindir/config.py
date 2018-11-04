import logging
import os
import asyncio
import json



class Config(object):
    POOL_NAME = "pool202"
    POOLGENESIS = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "ptgenesis")
    )
    PROTOCOL_VERSION = 2
    AGENTID = json.dumps({"id": os.getenv("AGENTID") if os.getenv("AGENTID") else "Agent"})
    AGENTKEY = json.dumps({"key": os.getenv("AGENTKEY") if os.getenv("AGENTKEY") else "SuperAgent!"})
    SEED = os.getenv("SEED") if os.getenv("SEED") else "000000000000000000000000Steward1"




