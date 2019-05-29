import base64
import logging
from .json_serializer import pack, unpack
from .message import Message
from ..agent import Agent
from indy import crypto, non_secrets, did

log = logging.getLogger(__name__)
class Connection:

    FAMILY_NAME = "connections"
    VERSION = "1.0"
    FAMILY = "did:dub:BzCbsNYhMrjHiqZDTUASHg;spec/" + FAMILY_NAME + "/" + VERSION + "/"

    INVITE = FAMILY + "invitation"
    REQUEST = FAMILY + "request"
    RESPONSE = FAMILY + "response"

    # def __init__(self, wallet_handle):
    #     self.handle = wallet_handle

    async def generate_dCard(self, owner, wallet_handle):
        try:
            agent = Agent()
            connection_key = await did.create_key(wallet_handle, "{}")

            invite_msg = Message(
                {
                    "@type": Connection.INVITE,
                    "from": owner,
                    "recipientKeys": [connection_key],
                    "serviceEndpoint": agent.agent_endpoint
                    # routingKeys not specified, but here is where they would be put in the invite.
                }
            )
            log.debug(invite_msg)

            await non_secrets.add_wallet_record(
                wallet_handle, "dCard", invite_msg["recipientKeys"][0], pack(invite_msg), "{}"
            )
            return invite_msg
        except Exception:
            log.exception(" Error generating dCard")
            raise
