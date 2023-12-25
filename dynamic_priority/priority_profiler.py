from framework.database.redisClient import RedisClient
class PriorityProfiler:
    def __init__(self, 
                 redis_read_key: str, 
                 redis_write_key: str, 
                 redis_host: str, 
                 redis_port: int, 
                 redis_db: int):
        self.redis_read_key = redis_read_key
        self.redis_write_key = redis_write_key
        self.redis_client = RedisClient(redis_host, redis_port, redis_db)

