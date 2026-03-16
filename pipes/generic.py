import multiprocessing as mp
import time


if __name__ == '__main__':
    workers = 5
    processes = []
    input_delay = 0.01
    queue_size = 50

    input_queue = mp.Queue(maxsize=queue_size)
    output_queue = mp.Queue(maxsize=queue_size)

    for _ in range(workers):
        p = mp.Process(target=worker, args=(input_queue, output_queue))A
        p.start()
        processes.append(p)

    time.sleep(input_delay)
    input_queue.put(1)
    input_queue.put(2)
    input_queue.put(3)

    for _ in range(workers):
        input_queue.put(None)

    for p in processes:
        p.join()

    packets = []
    while not output_queue.empty():
        packets.append(output_queue.get())

    print(f"Processed packets: {packets}")
