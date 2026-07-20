"""WebSocket example — one persistent connection, both sides talk anytime.

Self-contained demo: it starts a server, connects a client, they exchange
messages over a single long-lived connection, then close.

    pip install websockets
    python websocket_demo.py

Unlike the REST/webhook examples (one request, then done), the connection
here stays open — either side can send whenever it wants.
"""
import asyncio
import websockets


# ---- server: keeps the connection open, replies on the same socket ----
async def server_handler(websocket):
    async for message in websocket:            # loops for as long as it's open
        print(f"[server] got: {message}")
        await websocket.send(f"echo: {message}")   # server can push anytime


async def run_server():
    async with websockets.serve(server_handler, "localhost", 8765):
        await asyncio.Future()                 # keep serving forever


# ---- client: sends several messages over the SAME connection ----
async def run_client():
    async with websockets.connect("ws://localhost:8765") as ws:
        for text in ["hello", "still here", "bye"]:
            await ws.send(text)
            reply = await ws.recv()
            print(f"[client] got: {reply}")


async def main():
    server = asyncio.create_task(run_server())
    await asyncio.sleep(0.5)                    # give the server a moment
    await run_client()
    server.cancel()


if __name__ == "__main__":
    asyncio.run(main())
