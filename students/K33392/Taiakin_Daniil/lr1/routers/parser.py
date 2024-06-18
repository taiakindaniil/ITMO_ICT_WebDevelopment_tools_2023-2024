from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, status
import aiohttp
from celery import Celery
from celery.result import AsyncResult

from schemas import ParseRequest

router = APIRouter(prefix="/parse")
app = Celery("parser")

@router.post("")
async def parse(req: ParseRequest):
    async with aiohttp.ClientSession(trust_env=True) as client:
        async with client.post("http://parser-api:8080/parse", json=dict(req)) as resp:
            return await resp.json()


@router.post("/celery/sync")
def parse_celery_sync(req: ParseRequest):
    result = app.send_task("tasks.parse", args=[req.parser])
    return result.get(timeout=10)


@router.post("/celery/async")
def parse_async(req: ParseRequest):
    task = app.send_task("tasks.parse", args=[req.parser])
    return task.as_list()
