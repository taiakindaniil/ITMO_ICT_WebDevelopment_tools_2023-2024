import multiprocessing
from conn import get_session, init_db
from parser import AbstractParser, LabirintParser, Book24Parser

def parse_and_save(parser: AbstractParser):
    parsed_data = parser.parse()
    session = next(get_session())
    for d in parsed_data:
        session.add(d)
    session.commit()

def main():
    blockchain_parser = LabirintParser()
    btc_parser = Book24Parser()
    process1 = multiprocessing.Process(target=parse_and_save, args=(blockchain_parser,))
    process2 = multiprocessing.Process(target=parse_and_save, args=(btc_parser,))
    process1.start()
    process2.start()
    process1.join()
    process2.join()

if __name__ == "__main__":
    init_db()
    main()