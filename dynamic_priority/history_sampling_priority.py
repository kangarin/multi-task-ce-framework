import numpy as np

# 把history排序后，从小到大等分成priority_cnt份，以此来重新分配priority

class PriorityManager:
    def __init__(self, history_length: int = 1000, priority_cnt: int = 16):
        self.history_length = history_length
        # records for prediction, updated periodically
        self.history_records = []
        # priority threshold for each priority level
        self.priority_threshold = []
        # temporary new coming records to be merged into history_records
        self.history_records_buffer = []
        self.priority_cnt = priority_cnt
        self.first_time = True

    def add_record(self, priority: int):
        if self.first_time:
            self.history_records.append(priority)
            if len(self.history_records) >= self.history_length:
                self.history_records = self.history_records[-self.history_length:]
                history_records_sorted = sorted(self.history_records)
                self.priority_threshold = history_records_sorted[::len(history_records_sorted) // self.priority_cnt]
                self.first_time = False
                print(self.priority_threshold)
                print(self.history_records)
            return
        else:
            self.history_records_buffer.append(priority)
            if len(self.history_records_buffer) >= self.history_length / 2:
                self.history_records.extend(self.history_records_buffer)
                self.history_records = self.history_records[-self.history_length:]
                self.history_records_buffer = []
                history_records_sorted = sorted(self.history_records)
                self.priority_threshold = history_records_sorted[::len(history_records_sorted) // self.priority_cnt]
                print(self.priority_threshold)
                print(self.history_records)

    def get_new_priority(self, old_priority) -> int:
        if len(self.priority_threshold) == 0:
            return old_priority
        for i in range(len(self.priority_threshold)):
            if old_priority < self.priority_threshold[i]:
                return i
        return len(self.priority_threshold)
    
if __name__ == "__main__":
    priority_manager = PriorityManager(history_length=1000, priority_cnt=8)
    for i in range(1000):
        # priority_manager.add_record(np.random.randint(1, 9))
        # generate normal distribution
        priority_manager.add_record(np.random.normal(2, 1))

    print(priority_manager.get_new_priority(1))
    print(priority_manager.get_new_priority(2))
    print(priority_manager.get_new_priority(3))
    print(priority_manager.get_new_priority(4))
    print(priority_manager.get_new_priority(5))
    print(priority_manager.get_new_priority(6))
    print(priority_manager.get_new_priority(7))
    print(priority_manager.get_new_priority(8))