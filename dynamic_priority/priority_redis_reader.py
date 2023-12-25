import redis
import json

if __name__ == "__main__":
    # 创建 Redis 连接
    redis_host = 'localhost'
    redis_port = 6379
    redis_db = 0
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    
    redis_key = "statistics_key"

    # 检查有序集合的长度
    max_entries = 5
    current_length = redis_client.zcard(redis_key)

    # 如果超过最大条目数，执行截断操作
    if current_length > max_entries:
        items_to_remove = current_length - max_entries
        redis_client.zremrangebyrank(redis_key, 0, items_to_remove - 1)

    # 读取有序集合的所有成员
    all_members = redis_client.zrange(redis_key, 0, -1)

    for member_data in all_members:
        # 解析 JSON 数据
        statistics_data = json.loads(member_data.decode('utf-8'))

        # 在这里处理统计信息，可以将其存储到数据库、进行实时分析等
        print("Received statistics from", statistics_data["service_name"])
        print("Metrics:", statistics_data)
