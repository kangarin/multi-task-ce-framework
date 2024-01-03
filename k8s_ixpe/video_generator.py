# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from framework.service.generator import Generator
import cv2
from framework.message_queue.rabbitmq import RabbitmqPublisher
from framework.database.redisClient import RedisClient
import json
import base64
import time

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoGenerator(Generator):
    def __init__(self, 
                 init_parameters: dict,
                 data_source: object, 
                 id: str, 
                 source_name: str,
                 mq_topic: str, 
                 priority: int,
                 tuned_parameters_init: dict,
                 tuned_parameters_redis_key: str,
                 priority_redis_key: str,
                 rabbitmq_host: str = 'localhost', 
                 rabbitmq_port: int = 5672, 
                 rabbitmq_username: str ='guest', 
                 rabbitmq_password: str ='guest', 
                 rabbitmq_max_priority:int =10,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 redis_db: int = 0):
        super().__init__(data_source, id, mq_topic, priority, tuned_parameters_init)
        self.init_parameters = init_parameters
        self.publisher = RabbitmqPublisher(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, mq_topic, rabbitmq_max_priority)
        self.redis_client = RedisClient(redis_host, redis_port, redis_db)
        self._data_source = cv2.VideoCapture(data_source)
        self.tuned_parameters_redis_key = tuned_parameters_redis_key
        self.priority_redis_key = priority_redis_key
        self.source_name = source_name

    @classmethod
    def generator_type(cls) -> str:
        return 'video'

    @classmethod
    def generator_description(cls) -> str:
        return 'ixpe video generator'

    def get_data_source(self) -> object:
        return self._data_source

    def get_id(self) -> str:
        return self._id
    
    def get_mq_topic(self) -> str:
        return self._mq_topic

    def get_priority(self) -> int:
        return self._priority
    
    def set_priority(self, priority: int):
        self._priority = priority

    def get_tuned_parameters(self) -> dict:
        return self._tuned_parameters
    
    def set_tuned_parameters(self, tuned_parameters: dict):
        self._tuned_parameters = tuned_parameters

    def send_task_to_mq(self, task: VideoTask):
        # print(len(json.dumps(task.serialize())))
        self.publisher.publish(json.dumps(task.serialize()), task.get_priority())

    def run(self):
        # import random
        # while True:
        #     random_num = random.randint(0, 100)
        #     yield random_num

        id = 0
        cnt = 0
        
        frames_per_task = self.get_tuned_parameters()['frames_per_task']
        skipping_frame_interval = self.get_tuned_parameters()['skipping_frame_interval']
        temp_frame_buffer = []
        
        # 清除redis缓存的lps和rps，不然逻辑错误
        redis_key_prefix_for_lps_and_rps = "ixpe_" + self.source_name
        self.clear_redis_lps_and_rps(redis_key_prefix_for_lps_and_rps)
        while True:

            ret, frame = self._data_source.read()
            if not ret:
                break
            cnt += 1
            if cnt % skipping_frame_interval != 0:
                continue
            temp_frame_buffer.append(frame)
            if len(temp_frame_buffer) < frames_per_task:
                continue
            else:
                # compress all the frames in the buffer into a short video, send it as a task, and empty the buffer
                compressed_video = self.compress_frames(temp_frame_buffer)
                base64_frame = base64.b64encode(compressed_video).decode('utf-8')
                task = VideoTask(base64_frame, id, self.source_name, self.get_priority(), self.get_tuned_parameters())
                self.send_task_to_mq(task)
                print(f"Generated task {task.get_seq_id()} from source {task.get_source_id()} with priority {task.get_priority()}")
                id += 1
                temp_frame_buffer = []
                time.sleep(1)


            # base64_frame = base64.b64encode(frame).decode('utf-8')
            # task = VideoTask(base64_frame, id, self._id, self._priority)


            # import random
            # random_num = random.randint(0, 100)
            # task = VideoTask(random_num, id, self._id, self._priority)
            # self.send_task_to_mq(task)
            # id += 1
            # time.sleep(5)

    def compress_frames(self, frames):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        height, width, _ = frames[0].shape
        timestamp = time.time()
        temp_file_path = f'{timestamp}_temp_{self.get_id()}.mp4'
        out = cv2.VideoWriter(temp_file_path, fourcc, 30, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()
        with open(temp_file_path, 'rb') as f:
            compressed_video = f.read()
        # delete the temporary file
        os.remove(temp_file_path)
        return compressed_video
    
    def generate_random_priority(self, low=1, high=10):
        import random
        return random.randint(low, high)
    
    def clear_redis_lps_and_rps(self, data_source_redis_key):
        lps_key = f"{data_source_redis_key}_lps"
        rps_key = f"{data_source_redis_key}_rps"
        old_lps = self.redis_client.get(lps_key)
        old_rps = self.redis_client.get(rps_key)
        print(f"Redis keys {lps_key} and {rps_key} cleared, old lps: {old_lps}, old rps: {old_rps}")
        self.redis_client.delete(lps_key)
        self.redis_client.delete(rps_key)
        print(f"Redis keys {lps_key} and {rps_key} cleared")


if __name__ == '__main__':

# TODO: 初始化的时候从redis里面读取配置参数，需要在容器启动前把配置参数写入redis
# 目前是把初始化参数写死在环境变量里，在k8s里面启动容器的时候把环境变量传进去

    # def __init__(self, 
    #              data_source: object, 
    #              id: str, 
    #              mq_topic: str, 
    #              priority: int,
    #              tuned_parameters_init: dict,
    #              tuned_parameters_redis_key: str,
    #              rabbitmq_host: str = 'localhost', 
    #              rabbitmq_port: int = 5672, 
    #              rabbitmq_username: str ='guest', 
    #              rabbitmq_password: str ='guest', 
    #              rabbitmq_max_priority:int =10,
    #              redis_host: str = 'localhost',
    #              redis_port: int = 6379,
    #              redis_db: int = 0):


    import os
    init_parameters = json.loads(os.environ['INIT_PARAMETERS'])
    data_source = os.environ['DATA_SOURCE']
    id = os.environ['ID']
    source_name = os.environ['SOURCE_NAME']
    mq_topic = os.environ['RABBIT_MQ_QUEUE']
    priority = int(os.environ['INIT_PRIORITY'])
    tuned_parameters_init = json.loads(os.environ['TUNED_PARAMETERS_INIT'])
    tuned_parameters_redis_key = os.environ['TUNED_PARAMETERS_REDIS_KEY']
    priority_redis_key = os.environ['PRIORITY_REDIS_KEY']
    rabbit_mq_host = os.environ['RABBIT_MQ_IP']
    rabbit_mq_port = int(os.environ['RABBIT_MQ_PORT'])
    rabbit_mq_username = os.environ['RABBIT_MQ_USERNAME']
    rabbit_mq_password = os.environ['RABBIT_MQ_PASSWORD']
    max_priority = int(os.environ['RABBIT_MQ_MAX_PRIORITY'])
    redis_host = os.environ['REDIS_IP']
    redis_port = int(os.environ['REDIS_PORT'])
    redis_db = int(os.environ['REDIS_DB'])
    
    generator = VideoGenerator(init_parameters,
                               data_source, 
                               id, 
                               source_name,
                               mq_topic, 
                               priority, 
                               tuned_parameters_init, 
                               tuned_parameters_redis_key,
                               priority_redis_key, 
                               rabbit_mq_host, 
                               rabbit_mq_port, 
                               rabbit_mq_username, 
                               rabbit_mq_password, 
                               max_priority, 
                               redis_host, 
                               redis_port, 
                               redis_db)
    generator.run()

    # generator = VideoGenerator("/Users/wenyidai/GitHub/video-dag-manager/input/traffic-720p.mp4", f'generator_{id}',
    #                             'testapp/generator', 0, {"frames_per_task": 5, "skipping_frame_interval": 5})
    
    # generator = VideoGenerator(data_source, f'video_generator_{id}', mq_topic, max_priority, {"frames_per_task": 5, "skipping_frame_interval": 5}, rabbit_mq_host, rabbit_mq_port, rabbitmq_max_priority=max_priority)
    # generator.run()

