import time
import asyncio
from sum_threading import main as threading_main
from sum_multi import main as multi_main
from sum_async import main as async_main
from functools import partial

def benchmark(func, name):
    start_time = time.perf_counter()
    func()
    end_time = time.perf_counter()
    print(f"{name} ended in {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    benchmark(threading_main, "Threading")
    benchmark(multi_main, "Multiprocessing")
    benchmark(partial(asyncio.run, async_main()), "Asyncio")