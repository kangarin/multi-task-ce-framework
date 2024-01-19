from redis import StrictRedis

class RedisClient(object):
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.redis_client = StrictRedis(host=host, port=port, db=db)

    def set(self, key, value):
        self.redis_client.set(key, value)

    def get(self, key):
        return self.redis_client.get(key)
    
    def delete(self, key):
        self.redis_client.delete(key)



if __name__ == '__main__':
    redisClient = RedisClient(host='localhost', port=6379, db=0)
    redisClient.set('test_plain', 'test')
    print(redisClient.get('test_plain'))
    # open a json file

    #     {
    #     "test": "test",
    #     "test2": {
    #         "test3": "test3"
    #     },
    #     "test4": [
    #         "test5",
    #         "test6"
    #     ]
    # }

    import json
    with open('framework/database/testjson.json', 'r') as f:
        data = json.load(f)
    # convert it to a string
    data = json.dumps(data)
    # save it to redis
    redisClient.set('test_json', data)
    # get it back
    data = redisClient.get('test_json')

    print(json.loads(data))

    # change a value
    data = json.loads(data)
    data['test'] = 'test_changed'
    # save it back to redis
    data = json.dumps(data)
    redisClient.set('test_json', data)
    # get it back
    data = redisClient.get('test_json')

    print(json.loads(data))