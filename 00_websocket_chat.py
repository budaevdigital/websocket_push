import os
import logging

import asyncio
import websockets


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=int(os.environ.get("LOG_SOCKET")) if os.environ.get("LOG_SOCKET") else logging.INFO
)


peoples = {}


async def welcome(websocket: websockets.WebSocketServerProtocol) -> str:
    # запрос имени пользователя
    await websocket.send("Как вас зовут?")
    name = await websocket.recv()   # метод ожидает ответа
    await websocket.send("Для отправки сообщения укажите собеседника '<имя>: <сообщение>'. Например, Иван: Помнишь, что завтра дедлайн?!")
    await websocket.send("Для просмотра списка участников чата, введите '?'")
    peoples[name.strip()] = websocket
    logger.debug(f"{peoples=}")
    return name


async def receiver(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    name = await welcome(websocket)
    while True:
        # получаем сообщение и проверям по условию
        while True:
            message = (await websocket.recv()).strip()
            if message == "?":
                await websocket.send(", ".join(peoples.keys()))
                continue
            else:
                # парсим получателей сообщения
                to_people, text = message.split(": ", 1)
                if to_people in peoples:
                    # отсылаем сообщение получателю
                    await peoples[to_people].send(f"Сообщение от {name}: {text}")
                else:
                    await websocket.send(f"Пользователь {to_people} не найден")


ws_server = websockets.serve(receiver, "localhost", 8765)


loop = asyncio.get_event_loop()
loop.run_until_complete(ws_server)
loop.run_forever()  # не завершаем event_loop
