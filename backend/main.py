import asyncio
import random
import time
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from detector import analizar_linea

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clientes_conectados: list[WebSocket] = []
RUTA_LOG = "access.log"

UMBRAL_PETICIONES = 10
VENTANA_SEGUNDOS = 30

historial_peticiones: dict[str, list[float]] = {}
ultima_alerta_fuerza_bruta: dict[str, float] = {}

IPS_SIMULADAS = [
    "45.33.32.156",
    "185.220.101.45",
    "103.21.244.0",
    "196.251.55.13",
    "200.98.196.0",
    "77.88.55.66",
]

PAYLOADS_ATAQUE = [
    "GET /login?user=admin' OR 1=1-- HTTP/1.1",
    "GET /search?q=<script>alert(1)</script> HTTP/1.1",
    "GET /files/../../etc/passwd HTTP/1.1",
    "POST /upload; cat /etc/shadow HTTP/1.1",
    "GET /product?id=1 UNION SELECT username,password FROM users HTTP/1.1",
]


def geolocalizar_ip(ip: str) -> str:
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = r.json()
        return data.get("country", "Desconocido")
    except Exception:
        return "Desconocido"


def extraer_ip(linea: str) -> str:
    return linea.split(" ")[0] if linea.strip() else "0.0.0.0"


def revisar_fuerza_bruta(ip: str) -> int:
    """Registra la peticion y devuelve el numero de intentos detectados
    si se debe emitir alerta ahora, o 0 si no corresponde todavia."""
    ahora = time.time()
    marcas = historial_peticiones.setdefault(ip, [])
    marcas.append(ahora)
    marcas[:] = [t for t in marcas if ahora - t <= VENTANA_SEGUNDOS]

    if len(marcas) < UMBRAL_PETICIONES:
        return 0

    ultima = ultima_alerta_fuerza_bruta.get(ip, 0)
    if ahora - ultima < VENTANA_SEGUNDOS:
        return 0

    ultima_alerta_fuerza_bruta[ip] = ahora
    return len(marcas)


async def vigilar_log():
    with open(RUTA_LOG, "r") as f:
        f.seek(0, 2)
        while True:
            linea = f.readline()
            if not linea:
                await asyncio.sleep(0.5)
                continue

            ip = extraer_ip(linea)

            tipo_ataque = analizar_linea(linea)
            if tipo_ataque:
                pais = geolocalizar_ip(ip)
                await difundir_alerta({"ip": ip, "pais": pais, "tipo": tipo_ataque})

            num_intentos = revisar_fuerza_bruta(ip)
            if num_intentos > 0:
                pais = geolocalizar_ip(ip)
                await difundir_alerta({
                    "ip": ip,
                    "pais": pais,
                    "tipo": "Fuerza Bruta",
                    "intentos": num_intentos,
                })


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
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes_conectados.remove(websocket)


@app.post("/simular")
async def simular_ataque():
    ip = random.choice(IPS_SIMULADAS)
    payload = random.choice(PAYLOADS_ATAQUE)
    linea = f'{ip} - - [01/Jul/2026] "{payload}" 200\n'

    with open(RUTA_LOG, "a") as f:
        f.write(linea)

    return {"status": "ok", "linea": linea}


@app.post("/simular-rafaga")
async def simular_rafaga():
    ip = random.choice(IPS_SIMULADAS)

    with open(RUTA_LOG, "a") as f:
        for _ in range(12):
            f.write(f'{ip} - - [01/Jul/2026] "GET /login HTTP/1.1" 401\n')

    return {"status": "ok", "ip": ip}
