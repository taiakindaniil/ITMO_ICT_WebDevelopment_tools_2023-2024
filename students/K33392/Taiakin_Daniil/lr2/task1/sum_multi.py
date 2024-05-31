from multiprocessing import Pool

def calculate_sum(start, end):
    total = 0
    for i in range(start, end):
        total += i
    return total


def main():
    chunk_size = 10**5

    pool = Pool(processes=10**6 // chunk_size)
    result = [pool.apply(calculate_sum, (i+1, i+chunk_size+1)) for i in range(0, 10**6, chunk_size)]

    print("Result of sum:", sum(result))


if __name__ == "__main__":
    main()