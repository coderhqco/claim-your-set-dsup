from dsu.asgi import application
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
import pytest

TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class BillConsumerTestCase:

    async def test_consumer_create(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(application, "/ws/bill/6127/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # Test sending text
        message={
            "vote_type":"N",
            "username":"K3K7N"
        }
        # channel_layer = get_channel_layer()
        # await channel_layer.group_send('test', message=message)
        await communicator.send_json_to(message)
        response = await communicator.receive_json_from()
        
        # Close
        await communicator.disconnect()

    async def test_consumer_update(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(application, "/ws/bill/6127/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # Test sending text
        await communicator.send_json_to({"vote_type":"N","username":"B5B3L"})
        response = await communicator.receive_json_from()
        print(response)
        # Close
        await communicator.disconnect()

    async def test_consumer_no_bill(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(application, "/ws/bill/6127/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # Test sending text
        await communicator.send_json_to({"vote_type":"N","username":"B5B3L"})
        response = await communicator.receive_json_from()
        print(response)
        # Close
        await communicator.disconnect()