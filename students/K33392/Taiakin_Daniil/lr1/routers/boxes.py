from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_session

from models import Box
from schemas import BoxRead, BoxCreate, DeleteResponse

router = APIRouter(prefix="/boxes")

@router.get("/", response_model=list[BoxRead])
def read_boxes(skip: int = 0, limit: int = 100, db = Depends(get_session)):
    boxes = db.query(Box).offset(skip).limit(limit).all()
    return boxes


@router.get("/{box_id}", response_model=BoxRead)
def read_box(box_id: int, db = Depends(get_session)):
    book = db.query(Box).filter(Box.id == box_id).first()
    return book


@router.post("/", response_model=BoxRead)
def create_box(box: BoxCreate, db = Depends(get_session)):
    db_box = Box(**box.model_dump())
    db.add(db_box)
    db.commit()
    db.refresh(db_box)
    return db_box


@router.put("/{box_id}", response_model=BoxRead)
def update_box(box_id: int, updated_box: BoxCreate, db = Depends(get_session)) -> BoxRead:
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The box was not found")
    db.query(Box).filter(Box.id == box_id).update(updated_box.dict(exclude_unset=True),
                                                     synchronize_session=False)
    db.commit()
    db.refresh(box)
    
    return box


@router.delete("/{box_id}", response_model=DeleteResponse)
def delete_box(box_id: int, db = Depends(get_session)) -> DeleteResponse:
    box = db.query(Box).filter(Box.id == box_id).first()
    if not box:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The box was not found")
    db.delete(box)
    db.commit()
    return DeleteResponse(message="The box was deleted successfully")