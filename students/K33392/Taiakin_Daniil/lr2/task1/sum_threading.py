from threading import Thread

def calculate_sum(start, end, result):
    total = 0
    for i in range(start, end):
        total += i
    result.append(total)


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


if __name__ == "__main__":
    main()