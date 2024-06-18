from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from parser import LabirintParser, Book24Parser
from pydantic import BaseModel
from enum import Enum

app = FastAPI()


class ParserType(Enum):
    LABIRINT = "labirint"
    BOOK24 = "book24"

    def get_parser(self) -> LabirintParser | Book24Parser | None:
        if self.value == "labirint":
            return LabirintParser()
        if self.value == "book24":
            return Book24Parser()
        return None
        

class ParseRequest(BaseModel):
    parser: ParserType


@app.post("/parse")
async def parse(data: ParseRequest):
    if (parser := data.parser.get_parser()) is None:
        raise HTTPException(500, "Invalid parser specified")
    return [i.as_dict() for i in await parser.async_parse()]