# ActualDataRouters.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ActualDataForUser.ActualValuesData import ValuesDataContainer, HashedValue

actual_data_router = APIRouter(prefix="/actual_data", tags=["ActualData"])
value_vault = ValuesDataContainer()

connected_clients: list[WebSocket] = []
clients_query: dict[WebSocket, list[str]] = {}


@actual_data_router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    # Кожен новий клієнт починає з порожнім списком підписок
    clients_query[websocket] = []

    try:
        while True:
            data = await websocket.receive_json()

            if "update" in data:
                # Оновлюємо дані, отримані від одного з клієнтів
                values = [HashedValue(**v) for v in data["update"]]
                value_vault.update_values(values)

                # Підтвердження відправнику
                await websocket.send_text("Values updated successfully")

                # Відправляємо оновлення лише тим клієнтам, які підписані на ці теги
                for client in connected_clients:
                    # Пропускаємо відправника
                    if client == websocket:
                        continue

                    # Фільтруємо оновлені значення
                    tags_for_client = clients_query.get(client, [])
                    filtered_values = [v for v in values if v.tag in tags_for_client]

                    # Відправляємо, якщо є що відправляти
                    if filtered_values:
                        try:
                            await client.send_json([
                                {"tag": v.tag, "timestamp": v.timestamp, "value": v.value}
                                for v in filtered_values
                            ])
                        except Exception:
                            # Обробка помилок (наприклад, клієнт від'єднався)
                            pass

            elif "get" in data:
                # Зберігаємо список тегів, на які підписався клієнт
                tags_to_subscribe = data.get("get", [])
                clients_query[websocket] = tags_to_subscribe

                # Відправляємо поточні значення для підписаних тегів
                result = value_vault.get_many_values(tags_to_subscribe)

                await websocket.send_json([
                    {"tag": v.tag, "timestamp": v.timestamp, "value": v.value}
                    for v in result.values()
                ])

            elif "get_all" in data:
                # Клієнт просить усі актуальні значення
                clients_query[websocket] = []  # Очищаємо підписку, якщо була
                result = value_vault.get_all_values()
                await websocket.send_json([
                    {"tag": v.tag, "timestamp": v.timestamp, "value": v.value}
                    for v in result
                ])

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        # Очищаємо підписки від'єднаного клієнта
        if websocket in clients_query:
            del clients_query[websocket]