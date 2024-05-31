import threading
from conn import get_session, init_db
from parser import AbstractParser, LabirintParser, Book24Parser

def parse_and_save(parser: AbstractParser, session):
    parsed_data = parser.parse()
    for d in parsed_data:
        session.add(d)
    session.commit()

def main():
    labirint_parser = LabirintParser()
    book24_parser = Book24Parser()
    session = next(get_session())
    thread1 = threading.Thread(target=parse_and_save, args=(labirint_parser, session))
    thread2 = threading.Thread(target=parse_and_save, args=(book24_parser, session))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

if __name__ == "__main__":
    init_db()
    main()