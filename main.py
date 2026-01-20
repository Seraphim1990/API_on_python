#main.py
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse

from Routers.DeviceRouter import devices_router
from Routers.NodeRouters import nodes_router
from Routers.ValuesRouter import values_router
from Routers.DecodingTypeRouter import decoding_type_router
from Routers.ActualDataRouters import actual_data_router
from Routers.EventsRouter import events_router
from Routers.MeasuresRouter import measures_router

app = FastAPI()

#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],  # Дозволяє запити з будь-яких джерел
#    allow_credentials=True,
#    allow_methods=["*"],  # Дозволяє всі методи (GET, POST, PUT, DELETE тощо)
#    allow_headers=["*"],  # Дозволяє всі заголовки
#)
@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path("index.html")  # наприклад, у папці "static"
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)



app.include_router(devices_router)
app.include_router(nodes_router)
app.include_router(values_router)
app.include_router(decoding_type_router)
app.include_router(actual_data_router)
app.include_router(events_router)
app.include_router(measures_router)