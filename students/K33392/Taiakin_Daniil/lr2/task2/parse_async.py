import asyncio as aio
from async_conn import get_session, init_db
from sqlalchemy.ext.asyncio import AsyncSession
from parser import AbstractParser, LabirintParser, Book24Parser

async def parse_with_db_save(parser: AbstractParser, session: AsyncSession):
    parsed_data = await parser.async_parse()
    for d in parsed_data:
        session.add(d)
    await session.commit()

async def main():
    labirint_parser = LabirintParser()
    book24_parser = Book24Parser()
    session = await anext(get_session())
    task1 = aio.create_task(parse_with_db_save(labirint_parser, session))
    task2 = aio.create_task(parse_with_db_save(book24_parser, session))
    await aio.gather(task1, task2)

if __name__ == "__main__":
    aio.run(main())