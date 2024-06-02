from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_session

from models import Tag
from schemas import TagRead, TagCreate, DeleteResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
def read_tags(skip: int = 0, limit: int = 100, db = Depends(get_session)) -> [TagRead]:
    routes = db.query(Tag).offset(skip).limit(limit).all()
    return routes


@router.get("/{tag_id}", response_model=TagRead)
def read_tag(tag_id: int, db = Depends(get_session)) -> TagRead:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    return tag


@router.post("", response_model=TagRead)
def create_tag(tag: TagCreate, db = Depends(get_session)) -> TagRead:
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, updated_tag: TagCreate, db = Depends(get_session)) -> TagRead:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The box was not found")
    db.query(Tag).filter(Tag.id == tag_id).update(updated_tag.dict(exclude_unset=True),
                                                  synchronize_session=False)
    db.commit()
    db.refresh(tag)
    
    return tag


@router.delete("/{tag_id}", response_model=DeleteResponse)
def delete_tag(tag_id: int, db = Depends(get_session)) -> DeleteResponse:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The tag was not found")
    db.delete(tag)
    db.commit()
    return DeleteResponse(message="The tag was deleted successfully")