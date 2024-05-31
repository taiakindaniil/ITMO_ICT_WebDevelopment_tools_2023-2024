import asyncio

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


if __name__ == "__main__":
    asyncio.run(main())