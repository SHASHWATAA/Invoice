import asyncio
import time

import websockets
from main import invoice_generator
import json
from send_message import send_data


connected = set()
# Throttling configuration
message_delay = 0.5  # Delay between consecutive messages in seconds

async def server(websocket, path):
    # Register.
    connected.add(websocket)
    try:
        async for message in websocket:
            for conn in connected.copy():
                if message.split("@@@")[0] == 'run':
                    message = message.split("@@@")[1]
                    print(message)
                    canvas_days = json.loads(message)['Canvas Home Interiors']
                    cyrus_days = json.loads(message)['Cyrus Rugs']
                    await invoice_generator(canvas_days, cyrus_days)
                    # await conn.send(f'{message}')


                else:
                    # Throttle outgoing messages
                    await asyncio.sleep(message_delay)
                    await conn.send(f'{message}')
    except websockets.exceptions.ConnectionClosedOK as e:
        pass
    finally:
        # Unregister.
        connected.remove(websocket)


async def main():
    async with websockets.serve(server, "localhost", 5000):
        await asyncio.Future()  # run forever


asyncio.run(main())
