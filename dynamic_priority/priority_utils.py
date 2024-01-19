import json
import time
from redis import StrictRedis

import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    from Task_v2_impl import Task_v2_Impl as Task
else:
    from .Task_v2_impl import Task_v2_Impl as Task

# 任务优先级由紧急程度和重要程度共同决定
# 重要程度I：0.0 ~ 1.0，数值越大越重要
# 紧急程度U：0.0 ~ 1.0，数值越大越紧急
# 优先级P：0.0 ~ 1.0，数值越大越优先
# P = a * I + b * U, a + b = 1.0
# U = min( (task.current_time - task.start_time ) / ( task.deadline - task.start_time ), 1.0 )

class UrgencyProfiler:
    def __init__(self, 
                 max_entries: int,
                 cold_start_entries: int,
                 urgency_cnt: int,
                 redis_record_key: str, 
                 redis_urgency_threshold_key: str, 
                 redis_host: str, 
                 redis_port: int, 
                 redis_db: int):
        self.max_entries = max_entries
        self.cold_start_entries = cold_start_entries
        self.urgency_cnt = urgency_cnt
        self.redis_record_key = redis_record_key
        self.redis_urgency_threshold_key = redis_urgency_threshold_key
        self.redis_client = StrictRedis(redis_host, redis_port, redis_db)

        # 清空 Redis 中的记录
        self.clear_redis_records()
        self.clear_redis_urgency_threshold()

    def prune_records_and_get_latest_records(self):
        # 检查有序集合的长度
        current_length = self.redis_client.zcard(self.redis_record_key)
        print("set counts: " + str(current_length))

        # 如果超过最大条目数，执行截断操作
        if current_length > self.max_entries:
            items_to_remove = current_length - self.max_entries
            self.redis_client.zremrangebyrank(self.redis_record_key, 0, items_to_remove - 1)

        # 读取有序集合的所有成员
        all_members = self.redis_client.zrange(self.redis_record_key, 0, -1)
        return all_members
    
    def get_urgency_threshold(self, all_members):
        if len(all_members) < self.cold_start_entries:
            return None

        # 获取所有记录的紧急程度
        urgency_list = []
        for member_data in all_members:
            # 解析 JSON 数据
            statistics_data = json.loads(member_data.decode('utf-8'))
            urgency_list.append(statistics_data["urgency"])

        # 计算紧急程度阈值
        urgency_list_sorted = sorted(urgency_list)
        urgency_threshold = urgency_list_sorted[(self.urgency_cnt - 1)::len(urgency_list_sorted) // self.urgency_cnt]
        if len(urgency_threshold) < self.urgency_cnt:
            urgency_threshold.append(urgency_list_sorted[-1])
        return urgency_threshold
    
    def update_urgency_threshold(self, urgency_threshold):
        if urgency_threshold is None:
            return

        # 将紧急程度阈值写入 Redis
        self.redis_client.set(self.redis_urgency_threshold_key, json.dumps(urgency_threshold))

    def clear_redis_records(self):
        self.redis_client.delete(self.redis_record_key)
        
    def clear_redis_urgency_threshold(self):
        self.redis_client.delete(self.redis_urgency_threshold_key)


class UrgencyReporter:
    def __init__(self,
                 redis_record_key: str, 
                 redis_urgency_threshold_key: str, 
                 redis_host: str, 
                 redis_port: int, 
                 redis_db: int):
        self.redis_record_key = redis_record_key
        self.redis_urgency_threshold_key = redis_urgency_threshold_key
        self.redis_client = StrictRedis(redis_host, redis_port, redis_db)

    def get_urgency_threshold(self):
        # 从 Redis 读取紧急程度阈值
        urgency_threshold = self.redis_client.get(self.redis_urgency_threshold_key)
        if urgency_threshold is None:
            return None
        return json.loads(urgency_threshold.decode('utf-8'))
    
    # relative_remaining_time: 0.0 ~ 1.0   表示任务到期剩余时间的相对比例，比如开始时间为 0，截止时间为 10，当前时间为 7，则 relative_remaining_time = (10 - 7) / (10 - 0) = 0.3
    def get_urgency(self, relative_remaining_time):
        urgency_threshold = self.get_urgency_threshold()
        ratio = 1 / len(urgency_threshold)
        if urgency_threshold is None:
            return relative_remaining_time
        for i in range(1, len(urgency_threshold)):
            if relative_remaining_time < urgency_threshold[i]:
                return i * ratio
        return 1.0
    
    def report_new_record(self, statistics_data):
        # 生成时间戳
        # timestamp = int(time.time())
        # 生成高精度时间戳
        timestamp = time.time_ns()
        
        # 将统计信息转换为 JSON 格式并写入有序集合
        member_data = json.dumps(statistics_data)
        self.redis_client.zadd(self.redis_record_key, {member_data: timestamp})


class PriorityGenerator:
    def __init__(self, urgency_reporter: UrgencyReporter):
        self.urgency_reporter = urgency_reporter

    def calculate_task_priority(self, task_importance, task_urgency, importance_urgency_ratio):
        importance_weight = importance_urgency_ratio / (importance_urgency_ratio + 1)
        urgency_weight = 1 - importance_weight
        return importance_weight * task_importance + urgency_weight * task_urgency
    
    def update_task_metadata(self, task: Task, current_time: float):
        task_importance = task.get_importance()
        task_urgency = self.urgency_reporter.get_urgency((current_time - task.get_start_time()) / (task.get_deadline() - task.get_start_time()))
        task.set_urgency(task_urgency)
        task.set_priority(self.calculate_task_priority(task_importance, task_urgency, task.get_importance_urgency_ratio()))


if __name__ == "__main__":

    urgency_profiler = UrgencyProfiler(max_entries=100,
                                         cold_start_entries=50,
                                         urgency_cnt=10,
                                         redis_record_key="statistics_key",
                                         redis_urgency_threshold_key="urgency_threshold_key",
                                         redis_host="localhost",
                                         redis_port=6379,
                                         redis_db=0)
    urgency_reporter = UrgencyReporter(redis_record_key="statistics_key",
                                         redis_urgency_threshold_key="urgency_threshold_key",
                                         redis_host="localhost",
                                         redis_port=6379,
                                         redis_db=0)
    priority_generator = PriorityGenerator(urgency_reporter)
    

    import random

    for i in range(50):
        random_urg = random.randint(0, 3) * 0.1
        urgency_reporter.report_new_record({
            "service_name": "your_service_name",
            "urgency": random_urg,
            "metric1": 100,
            "metric2": 200,
            # 添加其他统计信息...
            "timestamp": time.time_ns(),
        })
        time.sleep(0.01)

    all_members = urgency_profiler.prune_records_and_get_latest_records()
    urgency_threshold = urgency_profiler.get_urgency_threshold(all_members)
    urgency_profiler.update_urgency_threshold(urgency_threshold)
    print(urgency_threshold)

    test_task = Task(data=None,
                        seq_id=0,
                        source_id="test",
                        importance=1.0,
                        urgency=0.5,
                        importance_urgency_ratio=0.5,
                        deadline=time.time() + 10,
                        start_time=time.time(),
                        priority=0)
    time.sleep(1)
    priority_generator.update_task_metadata(test_task, time.time())
    print("after sleep 1s: priority = " + str(test_task.get_priority()))
    time.sleep(1)
    priority_generator.update_task_metadata(test_task, time.time())
    print("after sleep 1s: priority = " + str(test_task.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task, time.time())
    print("after sleep 3s: priority = " + str(test_task.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task, time.time())
    print("after sleep 3s: priority = " + str(test_task.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task, time.time())
    print("after sleep 3s: priority = " + str(test_task.get_priority()))
    

    print("==========================================")

    for i in range(100):
        random_urg = random.randint(0, 6) * 0.1
        urgency_reporter.report_new_record({
            "service_name": "your_service_name",
            "urgency": random_urg,
            "metric1": 100,
            "metric2": 200,
            # 添加其他统计信息...
            "timestamp": time.time_ns(),
        })
        time.sleep(0.01)

    all_members = urgency_profiler.prune_records_and_get_latest_records()
    urgency_threshold = urgency_profiler.get_urgency_threshold(all_members)
    urgency_profiler.update_urgency_threshold(urgency_threshold)
    print(urgency_threshold)

    test_task2 = Task(data=None,
                        seq_id=0,
                        source_id="test",
                        importance=1.0,
                        urgency=0.5,
                        importance_urgency_ratio=0.5,
                        deadline=time.time() + 10,
                        start_time=time.time(),
                        priority=0)
    
    time.sleep(1)
    priority_generator.update_task_metadata(test_task2, time.time())
    print("after sleep 1s: priority = " + str(test_task2.get_priority()))
    time.sleep(1)
    priority_generator.update_task_metadata(test_task2, time.time())
    print("after sleep 1s: priority = " + str(test_task2.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task2, time.time())
    print("after sleep 3s: priority = " + str(test_task2.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task2, time.time())
    print("after sleep 3s: priority = " + str(test_task2.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task2, time.time())
    print("after sleep 3s: priority = " + str(test_task2.get_priority()))


    print("==========================================")

    for i in range(100):
        random_urg = random.randint(0, 10) * 0.1
        urgency_reporter.report_new_record({
            "service_name": "your_service_name",
            "urgency": random_urg,
            "metric1": 100,
            "metric2": 200,
            # 添加其他统计信息...
            "timestamp": time.time_ns(),
        })
        time.sleep(0.01)

    all_members = urgency_profiler.prune_records_and_get_latest_records()
    urgency_threshold = urgency_profiler.get_urgency_threshold(all_members)
    urgency_profiler.update_urgency_threshold(urgency_threshold)
    print(urgency_threshold)

    test_task3 = Task(data=None,
                        seq_id=0,
                        source_id="test",
                        importance=1.0,
                        urgency=0.5,
                        importance_urgency_ratio=0.5,
                        deadline=time.time() + 10,
                        start_time=time.time(),
                        priority=0)
    
    time.sleep(1)
    priority_generator.update_task_metadata(test_task3, time.time())
    print("after sleep 1s: priority = " + str(test_task3.get_priority()))
    time.sleep(1)
    priority_generator.update_task_metadata(test_task3, time.time())
    print("after sleep 1s: priority = " + str(test_task3.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task3, time.time())
    print("after sleep 3s: priority = " + str(test_task3.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task3, time.time())
    print("after sleep 3s: priority = " + str(test_task3.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task3, time.time())
    print("after sleep 3s: priority = " + str(test_task3.get_priority()))

    print("==========================================")

    for i in range(100):
        random_urg = random.randint(0, 5) * 0.1
        urgency_reporter.report_new_record({
            "service_name": "your_service_name",
            "urgency": random_urg,
            "metric1": 100,
            "metric2": 200,
            # 添加其他统计信息...
            "timestamp": time.time_ns(),
        })
        time.sleep(0.01)
        
    all_members = urgency_profiler.prune_records_and_get_latest_records()
    urgency_threshold = urgency_profiler.get_urgency_threshold(all_members)
    urgency_profiler.update_urgency_threshold(urgency_threshold)
    print(urgency_threshold)

    test_task4 = Task(data=None,
                        seq_id=0,
                        source_id="test",
                        importance=1.0,
                        urgency=0.5,
                        importance_urgency_ratio=0.5,
                        deadline=time.time() + 10,
                        start_time=time.time(),
                        priority=0)
    
    time.sleep(1)
    priority_generator.update_task_metadata(test_task4, time.time())
    print("after sleep 1s: priority = " + str(test_task4.get_priority()))
    time.sleep(1)
    priority_generator.update_task_metadata(test_task4, time.time())
    print("after sleep 1s: priority = " + str(test_task4.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task4, time.time())
    print("after sleep 3s: priority = " + str(test_task4.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task4, time.time())
    print("after sleep 3s: priority = " + str(test_task4.get_priority()))
    time.sleep(3)
    priority_generator.update_task_metadata(test_task4, time.time())
    print("after sleep 3s: priority = " + str(test_task4.get_priority()))