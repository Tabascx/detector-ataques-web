import asyncio
import websockets

async def escuchar():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("Conectado, esperando alertas...")
        while True:
            mensaje = await websocket.recv()
            print("ALERTA RECIBIDA:", mensaje)

asyncio.run(escuchar())
