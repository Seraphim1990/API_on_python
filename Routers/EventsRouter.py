from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ActualDataForUser.EventsData import EventDataContainer
from DataBase.schemas import EventUpdate, EventGet

events_router = APIRouter(prefix="/events", tags=["Events"])
value_vault = EventDataContainer()

connected_clients: list[WebSocket] = []
clients_query: dict[WebSocket, list[str]] = {}


@events_router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    clients_query[websocket] = []

    try:
        while True:
            data = await websocket.receive_json()

            if "update" in data:
                # Оновлюємо дані. Тут data["update"] - це вже словник
                payload = EventUpdate(**data)
                value_vault.update_event(payload.update)
                await websocket.send_text("Values updated successfully")
                # Відправляємо оновлення лише тим клієнтам, які підписані на ці теги
                for client in connected_clients:
                    if client == websocket:
                        continue
                    subscribed_tags = clients_query[client]
                    events_to_send = {
                        tag: payload.update[tag]
                        for tag in subscribed_tags if tag in payload.update
                    }
                    if events_to_send:
                        try:
                            await client.send_json(events_to_send)
                        except Exception:
                            pass

            elif "get" in data:
                # Зберігаємо список тегів, на які підписався клієнт
                payload = EventGet(**data)
                clients_query[websocket] = payload.get
                result = {
                    event_type: value_vault.get_event(event_type)
                    for event_type in payload.get
                }
                await websocket.send_json({"get_response": result})

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        if websocket in clients_query:
            del clients_query[websocket]