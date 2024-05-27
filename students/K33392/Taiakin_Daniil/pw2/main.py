from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select
from typing_extensions import TypedDict

from connection import get_session, init_db
from models import *

app = FastAPI()


class MessageResponse(TypedDict):
    message: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/warriors")
def warriors_list(session: Session = Depends(get_session)) -> list[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warriors/{warrior_id}", response_model=WarriorProfessions)
def warriors_get(warrior_id: int, session: Session = Depends(get_session)) -> list[Warrior]:
    return session.exec(select(Warrior).where(Warrior.id == warrior_id)).first()


@app.post("/warriors")
def warriors_create(warrior: Warrior, session: Session = Depends(get_session)) -> Warrior:
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.delete("/warriors/{warrior_id}")
def warrior_delete(warrior_id: int, session: Session = Depends(get_session)) -> MessageResponse:
    session.delete(session.get(Warrior, warrior_id))
    session.commit()
    return {"message": "deleted"}


@app.put("/warriors/{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior, session: Session = Depends(get_session)) -> Warrior:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    db_warrior.sqlmodel_update(warrior_data)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.post("/warriors/{warrior_id}/skills/{skill_id}", response_model=WarriorProfessions)
def warrior_append_skill(warrior_id: int, skill_id: int, session: Session = Depends(get_session)) -> Warrior:
    if (skill := session.exec(select(Skill).where(Skill.id == skill_id)).first()) is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, {"message": "skill was not found"})
    if (warrior := session.exec(select(Warrior).where(Warrior.id == warrior_id)).first()) is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, {"message": "warrior was not found"})
    warrior.skills.append(skill)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.delete("/warriors/{warrior_id}/skills/{skill_id}", response_model=WarriorProfessions)
def warrior_delete_skill(warrior_id: int, skill_id: int, session: Session = Depends(get_session)) -> Warrior:
    if (warrior := session.exec(select(Warrior).where(Warrior.id == warrior_id)).first()) is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, {"message": "warrior was not found"})
    if (skill_idx := next((i for i, j in enumerate(warrior.skills) if j.id == skill_id), None)) is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, {"message": "skill was not found"})
    warrior.skills.pop(skill_idx)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.get("/professions")
def get_professions(session: Session = Depends(get_session)) -> list[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/professions/{profession_id}")
def get_profession(profession_id: int, session: Session = Depends(get_session)) -> Profession:
    return session.exec(select(Profession).where(Profession.id == profession_id)).first()


@app.post("/professions")
def create_profession(profession: Profession, session: Session = Depends(get_session)) -> Profession:
    profession = Profession.model_validate(profession)
    session.add(profession)
    session.commit()
    session.refresh(profession)
    return profession


@app.put("/professions/{profession_id}")
def update_profession(
    profession_id: int, profession: Profession, session: Session = Depends(get_session)
) -> Profession:
    db_profession = session.get(Profession, profession_id)
    if not db_profession:
        raise HTTPException(status_code=404, detail="profession not found")
    profession_data = profession.model_dump(exclude_unset=True)
    db_profession.sqlmodel_update(profession_data)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession


@app.delete("/professions/{profession_id}")
def delete_profession(profession_id: int, session: Session = Depends(get_session)) -> MessageResponse:
    session.delete(session.get(Profession, profession_id))
    session.commit()
    return {"message": "deleted"}


@app.get("/skills")
def get_skills(session: Session = Depends(get_session)) -> list[Skill]:
    return session.exec(select(Skill)).all()


@app.get("/skills/{skill_id}")
def get_skill(skill_id: int, session: Session = Depends(get_session)) -> Skill:
    return session.exec(select(Skill).where(Skill.id == skill_id)).first()


@app.post("/skills")
def create_skill(skill: Skill, session: Session = Depends(get_session)) -> Skill:
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@app.put("/skills/{skill_id}")
def update_skill(skill_id: int, skill: Skill, session: Session = Depends(get_session)) -> Skill:
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db_skill.sqlmodel_update(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, session: Session = Depends(get_session)) -> MessageResponse:
    session.delete(session.get(Skill, skill_id))
    session.commit()
    return {"message": "Skill deleted"}