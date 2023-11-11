import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BillsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connected....")
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnected from bill ....")
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Process the received data (e.g., update vote counts in the database)
        # Send updated data back to the client
        await self.send(text_data=json.dumps(data))

    