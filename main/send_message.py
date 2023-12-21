import asyncio
import time
import nest_asyncio
nest_asyncio.apply()
import websockets


async def send_message(message, status):
    async with websockets.connect("ws://localhost:5000") as websocket:
        message = f"{message}: {status}"
        await websocket.send(message)

async def send_data(message, status):
    pass
    # asyncio.new_event_loop().run_until_complete(send_message(message, status))
    asyncio.get_event_loop().run_until_complete(send_message(message, status))
    print(message)
    time.sleep(2)
    # await asyncio.create_task(send_message(message, status))


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(send_message("test", "123"))

    # send_data("test", "123")
