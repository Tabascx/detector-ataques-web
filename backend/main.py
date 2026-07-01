import asyncio
import time
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from detector import analizar_linea

app = FastAPI()

# Permitir que Angular (localhost:4200) se conecte sin bloqueo CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clientes_conectados: list[WebSocket] = []
RUTA_LOG = "access.log"


def geolocalizar_ip(ip: str) -> str:
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = r.json()
        return data.get("country", "Desconocido")
    except Exception:
        return "Desconocido"


def extraer_ip(linea: str) -> str:
    # Asume formato estándar de log: la IP es el primer campo
    return linea.split(" ")[0] if linea.strip() else "0.0.0.0"


async def vigilar_log():
    """Lee el log linea a linea (como tail -f) y analiza cada una."""
    with open(RUTA_LOG, "r") as f:
        f.seek(0, 2)  # ir al final del archivo, ignorar historico
        while True:
            linea = f.readline()
            if not linea:
                await asyncio.sleep(0.5)
                continue

            tipo_ataque = analizar_linea(linea)
            if tipo_ataque:
                ip = extraer_ip(linea)
                pais = geolocalizar_ip(ip)
                alerta = {"ip": ip, "pais": pais, "tipo": tipo_ataque}
                await difundir_alerta(alerta)


async def difundir_alerta(alerta: dict):
    desconectados = []
    for cliente in clientes_conectados:
        try:
            await cliente.send_json(alerta)
        except Exception:
            desconectados.append(cliente)
    for c in desconectados:
        clientes_conectados.remove(c)


@app.on_event("startup")
async def iniciar_vigilancia():
    asyncio.create_task(vigilar_log())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clientes_conectados.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # mantiene la conexion viva
    except WebSocketDisconnect:
        clientes_conectados.remove(websocket)
