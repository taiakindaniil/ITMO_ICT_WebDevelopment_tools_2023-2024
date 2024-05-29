from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_session

from models import Crossing
from schemas import CrossingRead, CrossingCreate, DeleteResponse

router = APIRouter(prefix="/crossings")

@router.get("/", response_model=list[CrossingRead])
def list_crossings(skip: int = 0, limit: int = 100, db = Depends(get_session)):
    boxes = db.query(Crossing).offset(skip).limit(limit).all()
    return boxes


@router.get("/{crossing_id}", response_model=CrossingRead)
def read_crossing(crossing_id: int, db = Depends(get_session)):
    crossing = db.query(Crossing).filter(Crossing.id == crossing_id).first()
    if not crossing:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The crossing was not found")
    return crossing


@router.post("/", response_model=CrossingRead)
def create_crossing(crossing: CrossingCreate, db = Depends(get_session)) -> CrossingRead:
    db_crossing = Crossing(**crossing.model_dump())
    db.add(db_crossing)
    db.commit()
    db.refresh(db_crossing)
    return db_crossing


@router.delete("/{crossing_id}", response_model=DeleteResponse)
def delete_crossing(crossing_id: int, db = Depends(get_session)) -> DeleteResponse:
    crossing = db.query(Crossing).filter(Crossing.id == crossing_id).first()
    if not crossing:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The crossing was not found")
    db.delete(crossing)
    db.commit()
    return DeleteResponse(message="The crossing was deleted successfully")