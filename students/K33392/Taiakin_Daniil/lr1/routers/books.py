from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_session

from models import Book, BooksTags
from schemas import BookRead, BookCreate, DeleteResponse

router = APIRouter(prefix="/books")


@router.get("/", response_model=list[BookRead])
def list_books(skip: int = 0, limit: int = 100, db = Depends(get_session)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookRead)
def read_book(book_id: int, db = Depends(get_session)) -> BookRead:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The book was not found")
    return book


@router.post("/", response_model=BookRead)
def create_book(book: BookCreate, db = Depends(get_session)) -> BookRead:
    tag_ids = book.tag_ids
    del book.tag_ids
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    for tag_id in tag_ids:
        db_books_tags = BooksTags(book_id=db_book.id, tag_id=tag_id)
        db.add(db_books_tags)
        db.commit()

    return db_book


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, updated_book: BookCreate, db = Depends(get_session)) -> BookRead:
    tag_ids = updated_book.tag_ids
    del updated_book.tag_ids
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The book was not found")
    db.query(Book).filter(Book.id == book_id).update(updated_book.dict(exclude_unset=True),
                                                     synchronize_session=False)
    db.commit()
    db.refresh(book)

    db.query(BooksTags).filter(BooksTags.book_id == book_id).delete(synchronize_session=False)
    for tag_id in tag_ids:
        db_books_tags = BooksTags(book_id=book_id, tag_id=tag_id)
        db.add(db_books_tags)
        db.commit()

    return book


@router.delete("/{book_id}", response_model=DeleteResponse)
def delete_book(book_id: int, db = Depends(get_session)) -> DeleteResponse:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The book was not found")
    db.delete(book)
    db.commit()
    return DeleteResponse(message="The book was deleted successfully")