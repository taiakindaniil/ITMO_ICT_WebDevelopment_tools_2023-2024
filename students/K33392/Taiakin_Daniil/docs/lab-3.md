# Лабораторная работа #3

## Задание
Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

## Решение

### REST API для парсера

Напишем fast api приложения для парсера, чтобы можно было вызывать его по rest api. Для этого, создадим модель данных в виде enum, которую будем ожидать от клиента. Добавим эндпоинт `/parse`.

Данный эндпоинт принимает название парсера и в ответ выводит список книг.
```python
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from parser import LabirintParser, Book24Parser
from pydantic import BaseModel
from enum import Enum

app = FastAPI()


class ParserType(Enum):
    LABIRINT = "labirint"
    BOOK24 = "book24"

    def get_parser(self) -> LabirintParser | Book24Parser | None:
        if self.value == "labirint":
            return LabirintParser()
        if self.value == "book24":
            return Book24Parser()
        return None
        

class ParseRequest(BaseModel):
    parser: ParserType


@app.post("/parse")
async def parse(data: ParseRequest):
    if (parser := data.parser.get_parser()) is None:
        raise HTTPException(500, "Invalid parser specified")
    return [i.model_dump() for i in await parser.async_parse()]
```

### Эндпоинт для обращения к парсеру

Создадим эндпоинт в основном приложении, который будет обращаться к паресру для получения списка книг.
```python
@router.post("")
async def parse(req: ParseRequest):
    async with aiohttp.ClientSession() as client:
        async with client.post("http://parser-api:8080/parse", json=dict(req)) as resp:
            return await resp.json()
```

Теперь реализуем эндпоинты для синхронного и асинхронного выполнения задач в Celery.

Синхронный метод будет отправлять задачу в очередь и ожидать получения результата в течение 10 секунд.

Асинхронный эндпоинт создает задачу и возвращает список из идентификаторов.

```python
@router.post("/celery/sync")
def parse_celery_sync(req: ParseRequest):
    result = app.send_task("tasks.parse", args=[req.parser])
    return result.get(timeout=10)

@router.post("/celery/async")
def parse_async(req: ParseRequest):
    task = app.send_task("tasks.parse", args=[req.parser])
    return task.as_list()
```

Также создадим get-запрос, который возвращает результат парсинга или 202 ACCEPTED статус код в том случае, когда задача находится в процессе.

```python
@router.get("/celery/task")
def get_task_result(task_id: str):
    result = AsyncResult(task_id, app=app)
    if not result.ready():
        return Response(HTTPStatus.ACCEPTED)
    return result.get()
```


### Dockerfile для backend

Создадим Dockerfile с нужной настройкой для создания докер-образа. Данный файл устанавливает зависимости, копирует все файлы из рабочей директории и запускает сервер.

```Dockerfile
FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Dockerfile для парсера

Для парсера мы создадим `Dockerfile` и `Dockerfile.celery`. Первый для запуска REST API (он точно такой же, как и для backend), а второй для Celery.

Ниже предсталвен `Dockerfile.celery`.

```Dockerfile
FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENTRYPOINT [ "celery", "-A", "tasks", "worker", "--loglevel=INFO"]
```

### compose.yaml

```yaml
version: "3.9"
services:
  backend:
    build: "${PWD}/lr1"
    ports:
      - "8080:8080"
    environment:
      - SQLALCHEMY_DATABASE_URL=postgresql://postgres:password@db:5432/postgres
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  parser:
    build:
      context: "${PWD}/lr2/task2"
      dockerfile: Dockerfile.celery
    environment:
      - SQLALCHEMY_DATABASE_URL=postgresql://postgres:password@db:5432/postgres
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - db
      - redis
    
  parser-api:
    build:
      context: "${PWD}/lr2/task2"
      dockerfile: Dockerfile
    environment:
      - SQLALCHEMY_DATABASE_URL=postgresql://postgres:password@db:5432/postgres
    depends_on:
      - db
  
  db:
    image: postgres
    container_name: postgres_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=postgres
    ports:
      - "5433:5432"
  
  redis:
    image: redis
    environment:
      - ALLOW_EMPTY_PASSWORD=yes

volumes:
  postgres_data:
```