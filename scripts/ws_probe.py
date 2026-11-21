import asyncio
import json
import os
import sys

import websockets


async def main() -> None:
    conversation_id = sys.argv[1]
    key = os.environ["AGENT_SERVER_SESSION_API_KEY"]
    uri = f"ws://127.0.0.1:{os.environ.get('AGENT_SERVER_PORT', '8010')}/sockets/events/{conversation_id}"
    async with websockets.connect(uri, open_timeout=5) as socket:
        await socket.send(json.dumps({"type": "auth", "session_api_key": key}))
        try:
            message = await asyncio.wait_for(socket.recv(), timeout=5)
            print(f"websocket_received={str(message)[:200]}")
        except asyncio.TimeoutError:
            print("websocket_connected=true websocket_received=timeout")


if __name__ == "__main__":
    asyncio.run(main())
