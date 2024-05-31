# Лабораторная работа #2

## Задание

### Задача 1
Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 1000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.

#### Решение
В качестве `calculate_sum` представлена данная функция, которая суммирует часла в определенном промежутке. Данная функция присутствует во всех подходах реализации. Единственное, в `sum_multi` и `sum_async` нет третьего агрумента result, а просто возвращается переменная `total`.
```python
def calculate_sum(start, end, result):
    total = 0
    for i in range(start, end):
        total += i
    result.append(total)
```

##### Threading
Определям нужный нам отрезок, который мы хотим просуммировать. Далее разбивает его на чанки (10^5). Каждый чанк создается отдельный поток. А результат записывается в список `result`, который мы суммируем после исполнения всех потоков.
```python
def main():
    result = []
    threads = []
    chunk_size = 10**5

    for i in range(0, 10**6, chunk_size):
        t = Thread(target=calculate_sum, args=(i+1, i+chunk_size+1, result))

        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

    print("Result of sum:", sum(result))
```

##### Multiprocessing
Точно так же, как и в первой реализации, мы разбиваем отрезок чисел на чанки (10^5). В данном случае, мы создаем пул, где указываем количество процессов равным количеству получившихся чанков. Далее, в пуле активируем метод calculate_sum с аргументами и записываем результаты в список `result`.
```python
def main():
    chunk_size = 10**5

    pool = Pool(processes=10**6 // chunk_size)
    result = [pool.apply(calculate_sum, (i+1, i+chunk_size+1)) for i in range(0, 10**6, chunk_size)]

    print("Result of sum:", sum(result))
```

##### Asyncio
Объявляем `calculate_sum` как коротину. Затем, для каждого чанка создаем `Task` и записываем их в список, ожидая исполнения. Далее, просто выводим суммируемый список. 
```python
async def calculate_sum(start, end):
    total = 0
    for i in range(start, end):
        total += i
    return total

async def main():
    tasks = []
    chunk_size = 10**5

    for i in range(0, 10**6, chunk_size):
        task = asyncio.create_task(calculate_sum(i+1, i+chunk_size+1))
        tasks.append(task)

    result = await asyncio.gather(*tasks)
    
    print("Result of sum:", sum(result))
```

##### Benchmark
Напишем benchmark для замера эффективности разных подходов. Ниже представлена сама функция, принимающая функцию, исполняющую конкретный подход.
```python
def benchmark(func, name):
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    print(f"{name} ended in {end_time - start_time:.4f} seconds")
```

Далее, вызываем `benchmark` для каждого импортированного подхода.
```python
if __name__ == "__main__":
    benchmark(threading_main, "Threading")
    benchmark(multi_main, "Multiprocessing")
    benchmark(partial(asyncio.run, async_main()), "Asyncio")
```

В качестве результата получилось следующее.
```sh
Result of sum: 500000500000
Threading ended in 0.0294 seconds

Result of sum: 500000500000
Multiprocessing ended in 0.1709 seconds

Result of sum: 500000500000
Asyncio ended in 0.0272 seconds
```
Самым эффективным оказался `multiprocessing`.

### Задача 2
Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.

#### Решение

##### Класс паресров
Создадим абстрактый класс парсера, который определяет синхронный и асинхронный сетоды для парсинга книг.
```python
class AbstractParser(ABC):
    base_url: str

    @abstractmethod
    def parse(self) -> list[Book]:
        ...
    
    @abstractmethod
    async def async_parse(self) -> list[Book]:
        ...
```

Создадим базовый класс парсера, который будет определять методы для парсинга данных с ресурса.
```python
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
```

Создадим класс для парсинга книг с сайта [Лабирит](https://www.labirint.ru/books/).
```python
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
```

Создадим второй класс для парсинга книг с сайта [Book24](https://book24.ru/knigi-bestsellery/).
```python
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
```

##### Threading
В программе для парсинга при помощи потоков, в каждый поток мы передаем объект класса парсера и в данном потоке сохраняем результаты в базу данных.
```python
import threading
from conn import get_session, init_db
from parser import AbstractParser, LabirintParser, Book24Parser

def parse_with_db_save(parser: AbstractParser, session):
    parsed_data = parser.parse()
    for d in parsed_data:
        session.add(d)
    session.commit()

def main():
    labirint_parser = LabirintParser()
    book24_parser = Book24Parser()
    session = next(get_session())
    thread1 = threading.Thread(target=parse_with_db_save, args=(labirint_parser, session))
    thread2 = threading.Thread(target=parse_with_db_save, args=(book24_parser, session))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

if __name__ == "__main__":
    init_db()
    main()
```

##### Multiprocessing
В коде программы для парсинга данных из разных процессов нам необходимо создавать сессию переключения к базе данных внутри функции `parse_with_db_save`.
```python
import multiprocessing
from conn import get_session, init_db
from parser import AbstractParser, LabirintParser, Book24Parser

def parse_with_db_save(parser: AbstractParser):
    parsed_data = parser.parse()
    session = next(get_session())
    for d in parsed_data:
        session.add(d)
    session.commit()

def main():
    blockchain_parser = LabirintParser()
    btc_parser = Book24Parser()
    process1 = multiprocessing.Process(target=parse_with_db_save, args=(blockchain_parser,))
    process2 = multiprocessing.Process(target=parse_with_db_save, args=(btc_parser,))
    process1.start()
    process2.start()
    process1.join()
    process2.join()

if __name__ == "__main__":
    init_db()
    main()
```

##### Asyncio

В случае с асинхронным методом, нам нужно написать дополнительный код, который будет создавать асинхронное подключение к базе данных.
```python
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

engine = create_async_engine(os.environ["ASYNC_SQLALCHEMY_DATABASE_URL"])

asyncSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with asyncSessionLocal() as session:
        yield session
```

Далее, напишем код, который создаст несколько объектов `Task` и дождется их выполнения.
```python
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
```


##### Benchmark

Используем код из первого задания для замера эффективности программ.
```python
import time
import asyncio
from parse_threading import main as threading_main
from parse_multi import main as multi_main
from parse_async import main as async_main
from conn import init_db
from functools import partial

def benchmark(func, name):
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    print(f"{name} ended in {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    init_db()
    benchmark(threading_main, "Threading")
    benchmark(multi_main, "Multiprocessing")
    benchmark(partial(asyncio.run, async_main()), "Asyncio")
```

Вывод benchmark получился такой.
```sh
Threading ended in 1.7869 seconds

Multiprocessing ended in 1.9192 seconds

Asyncio ended in 1.6669 seconds
```

В этом задании решение с использованием библиотеки `multiprocessing` оказалось самым медленным. Это произошло из-за того, что количество сайтов было небольшим, и накладные расходы на создание новых процессов значительно повлияли на производительность.

`Threading` получился медленее чем asyncio, вероятнее всего, из-за переключения между потоками.