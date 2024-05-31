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

