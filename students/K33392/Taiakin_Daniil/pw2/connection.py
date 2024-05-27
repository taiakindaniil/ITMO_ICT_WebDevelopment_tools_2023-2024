from sqlmodel import SQLModel, Session, create_engine

# docker run --name pw2-postgres -p 5433:5432 -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=warriors_db -d postgres
db_url = 'postgresql://postgres:mysecretpassword@127.0.0.1:5433/warriors_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session