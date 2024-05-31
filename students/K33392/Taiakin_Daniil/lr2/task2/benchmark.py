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