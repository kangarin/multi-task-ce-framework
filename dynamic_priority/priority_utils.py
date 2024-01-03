import json
import time
from redis import StrictRedis

class PriorityProfiler:
    def __init__(self, 
                 max_entries: int,
                 cold_start_entries: int,
                 priority_cnt: int,
                 redis_record_key: str, 
                 redis_priority_threshold_key: str, 
                 redis_host: str, 
                 redis_port: int, 
                 redis_db: int):
        self.max_entries = max_entries
        self.cold_start_entries = cold_start_entries
        self.priority_cnt = priority_cnt
        self.redis_record_key = redis_record_key
        self.redis_priority_threshold_key = redis_priority_threshold_key
        self.redis_client = StrictRedis(redis_host, redis_port, redis_db)

        # 清空 Redis 中的记录
        self.clear_redis_records()
        self.clear_redis_priority_threshold()

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
    
    def get_priority_threshold(self, all_members):
        if len(all_members) < self.cold_start_entries:
            return None

        # 获取所有记录的优先级
        priority_list = []
        for member_data in all_members:
            # 解析 JSON 数据
            statistics_data = json.loads(member_data.decode('utf-8'))
            priority_list.append(statistics_data["priority"])

        # 计算优先级阈值
        priority_list_sorted = sorted(priority_list)
        priority_threshold = priority_list_sorted[::len(priority_list_sorted) // self.priority_cnt]
        return priority_threshold
    
    def update_priority_threshold(self, priority_threshold):
        if priority_threshold is None:
            return

        # 将优先级阈值写入 Redis
        self.redis_client.set(self.redis_priority_threshold_key, json.dumps(priority_threshold))

    def clear_redis_records(self):
        self.redis_client.delete(self.redis_record_key)
        
    def clear_redis_priority_threshold(self):
        self.redis_client.delete(self.redis_priority_threshold_key)


class PriorityReporter:
    def __init__(self,
                 redis_record_key: str, 
                 redis_priority_threshold_key: str, 
                 redis_host: str, 
                 redis_port: int, 
                 redis_db: int):
        self.redis_record_key = redis_record_key
        self.redis_priority_threshold_key = redis_priority_threshold_key
        self.redis_client = StrictRedis(redis_host, redis_port, redis_db)

    def get_priority_threshold(self):
        # 从 Redis 读取优先级阈值
        priority_threshold = self.redis_client.get(self.redis_priority_threshold_key)
        if priority_threshold is None:
            return None
        return json.loads(priority_threshold.decode('utf-8'))
    
    def get_new_priority(self, old_priority) -> int:
        priority_threshold = self.get_priority_threshold()
        if priority_threshold is None:
            return old_priority
        for i in range(len(priority_threshold)):
            if old_priority < priority_threshold[i]:
                return i
        return len(priority_threshold)
    
    def report_new_record(self, statistics_data):
        # 生成时间戳
        # timestamp = int(time.time())
        # 生成高精度时间戳
        timestamp = time.time_ns()
        
        # 将统计信息转换为 JSON 格式并写入有序集合
        member_data = json.dumps(statistics_data)
        self.redis_client.zadd(self.redis_record_key, {member_data: timestamp})


if __name__ == "__main__":

    priority_profiler = PriorityProfiler(max_entries=100,
                                         cold_start_entries=50,
                                         priority_cnt=10,
                                         redis_record_key="statistics_key",
                                         redis_priority_threshold_key="priority_threshold_key",
                                         redis_host="localhost",
                                         redis_port=6379,
                                         redis_db=0)
    priority_reporter = PriorityReporter(redis_record_key="statistics_key",
                                         redis_priority_threshold_key="priority_threshold_key",
                                         redis_host="localhost",
                                         redis_port=6379,
                                         redis_db=0)
    

    import random

    for i in range(100):
        random_pri = random.randint(0, 3)
        priority_reporter.report_new_record({
            "service_name": "your_service_name",
            "priority": random_pri,
            "metric1": 100,
            "metric2": 200,
            # 添加其他统计信息...
            "timestamp": time.time_ns(),
        })
        time.sleep(0.1)

    all_members = priority_profiler.prune_records_and_get_latest_records()
    priority_threshold = priority_profiler.get_priority_threshold(all_members)
    priority_profiler.update_priority_threshold(priority_threshold)
    print(priority_threshold)

    print("==========================================")
    for i in range(100):
        random_pri = random.randint(0, 10)
        priority_reporter.report_new_record({
            "service_name": "your_service_name",
            "priority": random_pri,
            "metric1": 100,
            "metric2": 200,
            # 添加其他统计信息...
            "timestamp": time.time_ns(),
        })
        time.sleep(0.1)
        
    all_members = priority_profiler.prune_records_and_get_latest_records()
    priority_threshold = priority_profiler.get_priority_threshold(all_members)
    priority_profiler.update_priority_threshold(priority_threshold)
    print(priority_threshold)