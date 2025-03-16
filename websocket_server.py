import asyncio
import websockets
import json

connected_clients = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            pass  # The frontend doesn’t send messages back, only receives them
    finally:
        connected_clients.remove(websocket)

async def send_emotion(emotion):
    if connected_clients:  # Ensure there are active clients
        payload = json.dumps({"emotion": emotion})
        await asyncio.gather(*(client.send(payload) for client in connected_clients))

start_server = websockets.serve(handler, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
