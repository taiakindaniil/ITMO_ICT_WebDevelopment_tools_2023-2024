from celery import Celery
from typing import Literal
from parser import LabirintParser, Book24Parser

app = Celery("parser")

@app.task
def parse(parser_type: Literal["labirint", "book24"]):
    parser = None
    if parser_type == "labirint":
        parser = LabirintParser()
    elif parser_type == "book24":
        parser = Book24Parser()

    return [i.as_dict() for i in parser.parse()]