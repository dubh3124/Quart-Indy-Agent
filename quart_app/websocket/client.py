import asyncio
import websockets
from quart import Blueprint, request

client = Blueprint('client', __name__)
@client.route('/send')
async def sendMessage():
    async with websockets.connect(
            request.args.get("websocketUrl")) as websocket:
        name = request.args.get('name')

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")
        return "message sent!"

