import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    from Task_v2_impl import Task_v2_Impl as Task
else:
    from .Task_v2_impl import Task_v2_Impl as Task

from queue import PriorityQueue as PQ
import threading

class LocalPriorityQueue:
    def __init__(self) -> None:
        self._queue = PQ()
        self.lock = threading.Lock()

    def put(self, task: Task) -> None:
        with self.lock:
            self._queue.put(task)

    def get(self) -> Task:
        with self.lock:
            if self._queue.empty():
                return None
            return self._queue.get()
        
    def size(self) -> int:
        with self.lock:
            return self._queue.qsize()
        

if __name__ == "__main__":
    import random
    import time
    import threading

    def producer(queue: LocalPriorityQueue, num: int):
        for i in range(num):
            task = Task([random.randint(0, 100)], 
                        i, 
                        'source_id', 
                        random.random(), 
                        random.random(), 
                        random.random(), 
                        random.random(), 
                        random.random(), 
                        random.randint(0, 100))
            queue.put(task)
            print(f'Producer ===> data: {task.get_seq_id()}, priority: {task.get_priority()}')
            time.sleep(random.random() * 0.1)

    def consumer(queue: LocalPriorityQueue, num: int):
        for i in range(num):
            while True:
                task = queue.get()
                if task is not None:
                    break
                time.sleep(0.1)
            print(f'Consumer: <=== data: {task.get_seq_id()}, priority: {task.get_priority()}')
            time.sleep(random.random())

    queue = LocalPriorityQueue()
    num = 100
    producer_thread = threading.Thread(target=producer, args=(queue, num))
    consumer_thread = threading.Thread(target=consumer, args=(queue, num))
    producer_thread.start()
    consumer_thread.start()
    producer_thread.join()
    consumer_thread.join()