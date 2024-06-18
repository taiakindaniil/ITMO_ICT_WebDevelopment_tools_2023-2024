from datetime import datetime
from pydantic import BaseModel
from typing import Literal

from models import BookConditionEnum

class ParseRequest(BaseModel):
    parser: Literal["labirint", "book24"]


class DeleteResponse(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None



class BoxBase(BaseModel):
    name: str
    address: str


class BoxCreate(BoxBase):
    pass


class BoxRead(BoxBase):
    id: int
    # routes: list[Route] = []

    class Config:
        orm_mode = True



class TagBase(BaseModel):
    name: str
    description: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int

    class Config:
        orm_mode = True



class BookBase(BaseModel):
    name: str
    author: str
    description: str


class BookCreate(BookBase):
    tag_ids: list[int]
    pass


class BookRead(BookBase):
    id: int
    tags: list[TagRead] = []

    class Config:
        orm_mode = True



class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    first_name: str
    last_name: str
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserBooksRead(BaseModel):
    books: list[BookRead] = []

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    first_name: str
    last_name: str


class BookOwnershipRead(BaseModel):
    book: BookRead
    user: UserRead
    edition_year: int
    condition: BookConditionEnum


class BookOwnershipCreate(BaseModel):
    edition_year: int
    condition: BookConditionEnum



class CrossingBase(BaseModel):
    pass


class CrossingCreate(CrossingBase):
    available_book_id: int
    owner_id: int
    recepient_id: int
    box_id: int


class CrossingRead(CrossingBase):
    id: int
    book: BookRead
    owner: UserRead
    recepient: UserRead
    box: BoxRead
    created_at: datetime

    class Config:
        orm_mode = True