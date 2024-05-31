import requests
import aiohttp
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from models import Book

class AbstractParser(ABC):
    base_url: str

    @abstractmethod
    def parse(self) -> list[Book]:
        ...
    
    @abstractmethod
    async def async_parse(self) -> list[Book]:
        ...
    
    @abstractmethod
    def _parse(self, soup: BeautifulSoup) -> list[Book]:
        ...


class BaseParser(AbstractParser):
    base_url: str

    def get_soup(self) -> BeautifulSoup:
        return BeautifulSoup(requests.get(self.base_url).text, "html.parser")

    async def async_get_soup(self) -> BeautifulSoup:
        async with aiohttp.ClientSession() as client:
            async with client.get(self.base_url) as resp:
                return BeautifulSoup(await resp.read(), "html.parser")

    def parse(self) -> list[Book]:
        return self._parse(self.get_soup())
    
    async def async_parse(self) -> list[Book]:
        return self._parse(await self.async_get_soup())


class LabirintParser(BaseParser):
    def __init__(self):
        self.base_url = "https://www.labirint.ru/books/"
    
    def _parse(self, soup: BeautifulSoup):
        el = soup.find_all("div", class_="product", attrs={"data-sgenre-name": "книга"} )
        
        parsed_books = []
        
        for book in el:
            name = book["data-name"]
            div_author = book.find("div", class_="product-author")
            if not div_author:
                continue
            author = div_author.find("a")["title"]
            description = book["data-first-genre-name"]

            parsed_books.append(
                Book(name=name, author=author, description=description)
            )
        
        return parsed_books
    

class Book24Parser(BaseParser):
    def __init__(self):
        self.base_url = "https://book24.ru/knigi-bestsellery/"
    
    def _parse(self, soup: BeautifulSoup):
        el = soup.find_all("div", class_="product-card__content")
        
        parsed_books = []
        
        for book in el:
            name = book.find("a")["title"]
            a_author = book.find("a", class_="author-list__item smartLink")
            if not a_author:
                continue
            author = a_author.text

            parsed_books.append(
                Book(name=name, author=author)
            )
        
        return parsed_books
