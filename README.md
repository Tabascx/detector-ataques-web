# Detector de Ataques Web

Sistema de monitorizacion de seguridad en tiempo real que detecta patrones de ataque del OWASP Top 10 (SQL Injection, XSS, Path Traversal, Command Injection) y comportamiento anomalo (fuerza bruta) analizando logs de servidor web, con un dashboard en vivo construido en Angular.

## Por que este proyecto

La mayoria de detectores de estudiante se limitan a buscar patrones con regex (deteccion basada en firmas). Este proyecto añade una segunda capa: **deteccion basada en comportamiento**, contando la frecuencia de peticiones por IP para identificar ataques de fuerza bruta que no contienen ningun payload malicioso reconocible — el mismo principio que usan los SOC reales para reducir falsos negativos.

## Arquitectura

- **Backend**: Python + FastAPI, lee el log en tiempo real (estilo `tail -f`), aplica reglas regex de deteccion por patron y un contador de frecuencia por IP para deteccion de fuerza bruta. Emite alertas via WebSocket.
- **Frontend**: Angular 20 (standalone, zoneless, Signals), se conecta al WebSocket y renderiza las alertas en vivo sin recargar la pagina. Incluye selector de idioma ES/EN.

## Funcionalidades

- Deteccion de SQL Injection, XSS, Path Traversal y Command Injection por patrones OWASP
- Deteccion de fuerza bruta por frecuencia de peticiones (10 intentos / 30s por IP)
- Geolocalizacion real de IPs atacantes via API externa
- Dashboard en tiempo real via WebSocket, con reconexion automatica
- Botones de simulacion integrados en el dashboard (ataque puntual y rafaga de fuerza bruta), sin necesidad de terminal
- Interfaz bilingue ES/EN

## Stack tecnico

| Capa | Tecnologia |
|---|---|
| Backend | Python 3, FastAPI, WebSockets, Requests |
| Frontend | Angular 20 (standalone, zoneless), Signals, SCSS |
| Deteccion | Regex (OWASP Top 10) + analisis de frecuencia por IP |
| Geolocalizacion | ip-api.com |

## Instalacion

### Requisitos
- Python 3.10+
- Node.js 18+
- Angular CLI

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1      # Windows
pip install fastapi uvicorn websockets requests watchdog
uvicorn main:app --reload
```

El servidor arranca en `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
ng serve
```

El dashboard esta disponible en `http://localhost:4200`.

### Probar sin trafico real

El dashboard incluye dos botones para generar actividad de prueba sin necesidad de un servidor web real:

- **Simular Ataque**: escribe una linea de ataque aleatoria (SQLi, XSS, Path Traversal o Command Injection) desde una IP aleatoria del pool de pruebas.
- **Rafaga**: escribe 12 peticiones rapidas desde la misma IP, para disparar la deteccion de fuerza bruta.

## Decisiones tecnicas

**Por que WebSocket y no polling HTTP**: las alertas deben aparecer en tiempo real sin que el cliente tenga que preguntar constantemente "¿hay algo nuevo?". WebSocket mantiene una conexion abierta y el servidor empuja los datos en cuanto se detectan.

**Por que deteccion por frecuencia ademas de por patron**: un ataque de fuerza bruta contra un formulario de login no contiene ningun contenido malicioso reconocible por regex — son peticiones legitimas repetidas muchas veces. Solo se detecta observando el comportamiento a lo largo del tiempo, no el contenido de una peticion aislada.

**Por que Angular Signals en vez de RxJS/Subject**: el proyecto se genero en modo zoneless, para el cual Signals es el enfoque recomendado por el equipo de Angular. Los `computed()` recalculan automaticamente sin necesidad de suscripciones manuales ni `ngOnChanges`.

**Por que agregar alertas de fuerza bruta en vez de emitir una por peticion**: emitir una alerta por cada una de las 12 peticiones saturaria al analista con ruido repetido del mismo evento (alert fatigue). El sistema consolida el patron completo en una sola alerta con el conteo de intentos.

## Posibles mejoras futuras

- Persistencia de alertas en base de datos (SQLite/PostgreSQL)
- Tests unitarios con pytest para el modulo de deteccion
- Exportacion de alertas a CSV
- Dockerizacion completa (backend + frontend)
- Panel de severidad configurable por el usuario

## Autor

Proyecto desarrollado como parte de la formacion en Desarrollo de Aplicaciones Web (DAW), explorando la interseccion entre desarrollo frontend/backend y ciberseguridad defensiva.
