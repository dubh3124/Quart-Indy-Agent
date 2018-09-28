from quart import websocket, Blueprint

websoc = Blueprint('websoc', __name__)

@websoc.websocket('/connectionrequest')
async def ws():
    while True:
        await websocket.receive()
        await websocket.send("Received!")