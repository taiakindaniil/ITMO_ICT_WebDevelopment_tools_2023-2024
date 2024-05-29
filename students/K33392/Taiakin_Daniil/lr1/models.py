from enum import Enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class BookConditionEnum(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    VERY_GOOD = "very_good"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(String, index=True)

    tags = relationship("Tag", secondary="books_tags")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    registration_date = Column(DateTime(timezone=True), server_default=func.now())

    books = relationship(Book, secondary="book_ownership")


class Box(Base):
    __tablename__ = "boxes"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    address = Column(String, index=True)


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

    # books = relationship("Book", secondary="books_tags")


class BooksTags(Base):
    __tablename__ = "books_tags"

    book_id = Column(Integer, ForeignKey('books.id'), primary_key = True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key = True)


class BookOwnership(Base):
    __tablename__ = "book_ownership"

    # id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), primary_key = True)
    edition_year = Column(Integer)
    condition = Column(SQLEnum(BookConditionEnum))

    # book = relationship("Book", foreign_keys=[book_id])
    # user = relationship("User", foreign_keys=[user_id])


class Crossing(Base):
    __tablename__ = "crossings"

    id = Column(Integer, primary_key=True)
    available_book_id = Column(Integer, ForeignKey('books.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    recepient_id = Column(Integer, ForeignKey('users.id'))
    box_id = Column(Integer, ForeignKey('boxes.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    book = relationship("Book", foreign_keys=[available_book_id])
    owner = relationship("User", foreign_keys=[owner_id])
    recepient = relationship("User", foreign_keys=[recepient_id])
    box = relationship("Box", foreign_keys=[box_id])