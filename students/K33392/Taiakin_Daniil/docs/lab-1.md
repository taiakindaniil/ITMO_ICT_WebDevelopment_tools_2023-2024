# Лабораторная работа #1

## Практические работы
- [Практическая работа 1](../pw1/)
- [Практическая работа 2](../pw2/)
- [Практическая работа 3](../pw3/)


## Задание

Cоздать веб-приложение, которое позволит пользователям обмениваться книгами между собой. Это приложение должно облегчать процесс обмена книгами, позволяя пользователям находить книги, которые им интересны, и находить новых пользователей для обмена книгами.

Функционал веб-приложения должен включать следующее:

- **Создание профилей**: Возможность пользователям создавать профили, указывать информацию о себе, своих навыках, опыте работы и предпочтениях по проектам.
- **Добавление книг в библиотеку**: Пользователи могут добавлять книги, которыми они готовы поделиться, в свою виртуальную библиотеку на платформе.
- **Поиск и запросы на обмен**: Функционал поиска книг в библиотеке других пользователей. Возможность отправлять запросы на обмен книгами другим пользователям.
- **Управление запросами и обменами**: Возможность просмотра и управления запросами на обмен. Возможность подтверждения или отклонения запросов на обмен.


## Структура проекта

```
.
├── alembic.ini
├── database.py
├── dependencies
│   ├── __init__.py
│   ├── auth.py
│   └── hashing.py
├── main.py
├── migrations
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
├── models.py
├── requirements.txt
├── routers
│   ├── __init__.py
│   ├── auth.py
│   ├── books.py
│   ├── boxes.py
│   ├── crossings.py
│   ├── tags.py
│   └── users.py
└── schemas.py
```


## Ход работы

### Модели данных
Перед описанием самих моделей, была составлена схема базы данных со связями many-to-many и one-to-many.
![image](DB-schema%20for%20Web-ICT.jpg)

Для описания моделей была использована библиотека SQLAlchemy.

Создадим сущность книги со следующими полями. У данной сущности есть связь с тэгами.
```python
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    author = Column(String, index=True)
    description = Column(String, index=True)

    tags = relationship("Tag", secondary="books_tags")
```

Таблица для хранения пользователей выглядит следующим образом. Важно учесть, что поле `email` будет уникальным. У пользователя есть связь с тем, какие книги он может иметь. Поле `registration_date` автоматически записывается. 
```python
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
```

Так как создаем сервис для буккросинга, то есть некие боксы, в которых и происходит обмен книг.
```python
class Box(Base):
    __tablename__ = "boxes"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    address = Column(String, index=True)
```

Таблица тэгов описана следующим образом.
```python
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
```

В данной таблице мы связываем книги и тэги, образовывая связь many-to-many.
```python
class BooksTags(Base):
    __tablename__ = "books_tags"

    book_id = Column(Integer, ForeignKey('books.id'), primary_key = True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key = True)
```

В данной книге мы записываем владение книг пользователями.
```python
class BookOwnership(Base):
    __tablename__ = "book_ownership"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'), primary_key = True)
    edition_year = Column(Integer)
    condition = Column(SQLEnum(BookConditionEnum))
```

Здесь представлена таблица самих кроссингов (транзакции обмена книг).
```python
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
```

### API

В качестве примера эндпоинтов и реализации CRUD, возьмем книги.

Для разделения логики, воспользуемся классом `APIRouter`. При инициализации данного класса, указываем префикс `/books`, чтобы не указывать префиксный путь в последующих эндпоинтов.
```python
router = APIRouter(prefix="/books")
```

Далее предсталены модели pydentic, которые используются для ответов сервера и получения данных.
```python
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
```

Для создания книги представлен следующий POST эндпоинт.
```python
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
```

Для отображения всех книг, данный эднпоинт.  
```python
@router.get("/", response_model=list[BookRead])
def list_books(skip: int = 0, limit: int = 100, db = Depends(get_session)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books
```

Для отображения конкретной книги по id.  
```python
@router.get("/{book_id}", response_model=BookRead)
def read_book(book_id: int, db = Depends(get_session)) -> BookRead:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The book was not found")
    return book
```

Обновление книги выглядит следующим образом.
```python
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
```

Эндпоинт для удаления книги.
```python
@router.delete("/{book_id}", response_model=DeleteResponse)
def delete_book(book_id: int, db = Depends(get_session)) -> DeleteResponse:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="The book was not found")
    db.delete(book)
    db.commit()
    return DeleteResponse(message="The book was deleted successfully")
```

### JWT
Для реализации JWT-токенов в приложении были использованы следующие библиотеки: `pyjwt`, `passlib`.
Последняя нужна для хэширвоания паролей при помощи алгоритма `HS256`, где указывается секретный ключ.

Далее прдсталвена логика верификации и хэширования паролей.
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password) -> str:
    return pwd_context.hash(plain_password)
```

На следующем сниппете кода представлена логика генерирования JWT-токена.
```python
import os
from dotenv import load_dotenv
from jose import jwt

from datetime import datetime, timedelta, timezone

load_dotenv()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SECRET_KEY"], algorithm="HS256")
    return encoded_jwt
```

Здесь предсталвена логика аутентификации пользователя с учетом проверки на валидность введеного пароля и генерацией JWT-токена.
```python
@router.post("")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_session)
) -> Token:
    
    def authenticate_user(db, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
```


Здесь указана зависимость, которая используется для расшифровки и проверки JWT-токена с последующим получением вошедшего пользователя.
```python
async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user
```

### Alembic
Настроим работу с миграциями БД при помощи библиотеки `alembic`
```
alembic init migrations & alembic upgrade head
```