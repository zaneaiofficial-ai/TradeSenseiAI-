import asyncio
import base64
import websockets
import json

async def send_image(path, uri='ws://127.0.0.1:8000/ws'):
    with open(path, 'rb') as f:
        b = f.read()
    b64 = base64.b64encode(b).decode('ascii')
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({'type':'frame','data':b64}))
        resp = await ws.recv()
        print('Response:', resp)

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'test_frame.png'
    asyncio.run(send_image(path))
