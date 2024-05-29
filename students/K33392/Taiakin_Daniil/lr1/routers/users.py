from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from dependencies import hash_password
from database import get_session

from models import User, Book, BookOwnership
from schemas import UserCreate, UserRead, UserUpdate, DeleteResponse, UserBooksRead, BookRead, BookOwnershipCreate

from .auth import get_current_user

router = APIRouter(prefix="/users")


@router.get("/me/", response_model=UserRead)
async def get_current_active_user(
    current_user: UserRead = Depends(get_current_user)
) -> UserRead:
    if current_user.is_active == False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db = Depends(get_session)) -> UserRead:
    hashed_password = hash_password(user.password)
    del user.password
    db_user = User(**user.model_dump(), hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put("/", response_model=UserRead)
def update_me(updated_user: UserUpdate, db = Depends(get_session), current_user: UserRead = Depends(get_current_user)) -> UserRead:
    user = db.query(User).filter(User.id == current_user.id).first()
    db.query(User).filter(User.id == current_user.id).update(updated_user.dict(exclude_unset=True),
                                                             synchronize_session=False)
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/", response_model=DeleteResponse)
def delete_me(db = Depends(get_session), current_user: UserRead = Depends(get_current_user)) -> DeleteResponse:
    user = db.query(User).filter(User.id == current_user.id).first()
    db.delete(user)
    db.commit()
    return DeleteResponse(message="Your account was deleted successfully")


@router.get("/me/books", response_model=UserBooksRead)
def get_me_books(current_user: UserRead = Depends(get_current_user)) -> UserBooksRead:
    return current_user


@router.post("/me/books/add/{book_id}", response_model=BookRead)
def add_me_book(book_id: int, book_ownership: BookOwnershipCreate, db = Depends(get_session), current_user: UserRead = Depends(get_current_user)) -> BookRead:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The book was not found")
    
    db_book_ownership = BookOwnership(**book_ownership.model_dump(), book_id = book_id, user_id = current_user.id)
    db.add(db_book_ownership)
    db.commit()

    return book