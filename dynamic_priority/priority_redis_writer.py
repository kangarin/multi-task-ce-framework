import redis
import json
import time

if __name__ == "__main__":
    # 创建 Redis 连接
    redis_host = 'localhost'
    redis_port = 6379
    redis_db = 0
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    # 统计信息示例
    statistics_data = {
        "service_name": "your_service_name",
        "metric1": 100,
        "metric2": 200,
        # 添加其他统计信息...
        "timestamp": int(time.time()),
    }

    # 生成时间戳
    timestamp = int(time.time())

    # 将统计信息转换为 JSON 格式并写入有序集合
    redis_key = "statistics_key"
    member_data = json.dumps(statistics_data)
    redis_client.zadd(redis_key, {member_data: timestamp})

    print("Statistics sent to Redis.")
