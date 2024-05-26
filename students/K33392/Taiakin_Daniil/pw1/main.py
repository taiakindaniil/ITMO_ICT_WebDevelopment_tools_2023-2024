from enum import Enum
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from typing_extensions import TypedDict

app = FastAPI()


temp_bd = {
    "warriors": [
        {
            "id": 1,
            "race": "director",
            "name": "Мартынов Дмитрий",
            "level": 12,
            "profession_id": 1,
            "skills": [
                {"id": 1, "name": "Купле-продажа компрессоров", "description": ""},
                {"id": 2, "name": "Оценка имущества", "description": ""},
            ],
        },
        {
            "id": 2,
            "race": "worker",
            "name": "Андрей Косякин",
            "level": 12,
            "profession_id": 2,
            "skills": [],
        },
    ],
    "professions": [
        {"id": 1, "title": "Программист", "description": "Просто программист"},
        {"id": 2, "title": "Колдун", "description": "Вселяет чары каждому встречному"},
    ],
}


class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class Profession(BaseModel):
    id: int
    title: str
    description: str


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession_id: int
    skills: Optional[list[Skill]] = []


@app.get("/warriors")
def warriors_list() -> list[Warrior]:
    return temp_bd["warriors"]


@app.get("/warriors/{warrior_id}")
def warriors_get(warrior_id: int) -> list[Warrior]:
    return [warrior for warrior in temp_bd["warriors"] if warrior.get("id") == warrior_id]


@app.post("/warriors")
def warriors_create(warrior: Warrior) -> Warrior:
    temp_bd["warriors"].append(warrior.dict())
    return warrior


@app.delete("/warriors/{warrior_id}")
def warrior_delete(warrior_id: int) -> TypedDict("Response", {"message": str}):
    for i, warrior in enumerate(temp_bd["warriors"]):
        if warrior.get("id") == warrior_id:
            temp_bd["warriors"].pop(i)
            break
    return {"message": "deleted"}


@app.put("/warriors/{warrior_id}")
def warrior_update(warrior_id: int, warrior: dict) -> Warrior:
    for i, war in enumerate(temp_bd["warriors"]):
        if war.get("id") == warrior_id:
            temp_bd["warriors"][i] = warrior
    return temp_bd


@app.get("/professions")
def get_professions() -> list[Profession]:
    return temp_bd["professions"]


@app.get("/professions/{profession_id}")
def get_profession(profession_id: int) -> Profession:
    for profession in temp_bd["professions"]:
        if profession["id"] == profession_id:
            return profession
    raise HTTPException(status_code=404, detail="Profession not found")


@app.post("/professions")
def create_profession(profession: Profession) -> Profession:
    temp_bd["professions"].append(profession.dict())
    return profession


@app.put("/professions/{profession_id}")
def update_profession(profession_id: int, profession: Profession) -> Profession:
    for prof in temp_bd["professions"]:
        if prof["id"] == profession_id:
            prof.update(profession.dict())
            return profession
    raise HTTPException(status_code=404, detail="The profession was not found")


@app.delete("/professions/{profession_id}")
def delete_profession(profession_id: int) -> TypedDict("Response", {"message": str}):
    for i, prof in enumerate(temp_bd["professions"]):
        if prof["id"] == profession_id:
            temp_bd["professions"].pop(i)
            return {"message": "The specified profession was deleted successfully"}
    raise HTTPException(status_code=404, detail="The profession was not found")