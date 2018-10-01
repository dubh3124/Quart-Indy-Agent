import asyncio
import websockets


class WebsocketClient:
    def __init__(self, url):
        self.url = url

    async def sendMessage(self, payload):
        async with websockets.connect(self.url) as websocket:
            await websocket.send(payload)

            return await websocket.recv()
