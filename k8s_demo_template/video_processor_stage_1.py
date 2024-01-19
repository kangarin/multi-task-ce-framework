# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.processor import Processor
from framework.message_queue.rabbitmq import RabbitmqPublisher, RabbitmqSubscriber
from framework.database.redisClient import RedisClient
import json
import logging
import time
import cv2
import base64
import numpy as np
import threading
import random
from queue import PriorityQueue as PQ

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoProcessor1(Processor):
    def __init__(self, 
                 init_parameters: dict,
                 id: str, 
                 incoming_mq_topic: str, 
                 outgoing_mq_topic: str, 
                 priority: int, 
                 tuned_parameters_init: dict,
                 tuned_parameters_redis_key: str,
                 priority_redis_key: str,
                 rabbitmq_host: str = 'localhost', 
                 rabbitmq_port: int = 5672, 
                 rabbitmq_username:str = 'guest', 
                 rabbitmq_password: str = 'guest',
                 rabbitmq_max_priority: int = 10,                 
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 redis_db: int = 0):
        super().__init__(id, incoming_mq_topic, outgoing_mq_topic, priority, tuned_parameters_init)
        self.init_parameters = init_parameters
        self.subscriber = RabbitmqSubscriber(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, incoming_mq_topic, rabbitmq_max_priority)
        self.publisher = RabbitmqPublisher(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, outgoing_mq_topic, rabbitmq_max_priority)
        # This will be accessed by different threads, so we need to use a lock
        self.lock = threading.Lock()
        self.local_task_queue = PQ()
        self.redis_client = RedisClient(redis_host, redis_port, redis_db)
        self.tuned_parameters_redis_key = tuned_parameters_redis_key
        self.priority_redis_key = priority_redis_key

    @classmethod
    def processor_type(cls) -> str:
        return 'video'

    @classmethod
    def processor_description(cls) -> str:
        return 'Video processor1'

    def get_id(self) -> str:
        return self._id
    
    def get_incoming_mq_topic(self) -> str:
        return self._incoming_mq_topic

    def get_outgoing_mq_topic(self) -> str:
        return self._outgoing_mq_topic

    def get_priority(self) -> int:
        return self._priority
    
    def set_priority(self, priority: int):
        self._priority = priority

    def get_tuned_parameters(self) -> dict:
        return self._tuned_parameters
    
    def set_tuned_parameters(self, tuned_parameters: dict):
        self._tuned_parameters = tuned_parameters

    def get_task_from_incoming_mq(self) -> VideoTask:
        with self.lock:
            task = self.local_task_queue.get()
            return task

    def send_task_to_outgoing_mq(self, task: VideoTask):
        self.publisher.publish(json.dumps(task.serialize()), task.get_priority())

    def run(self):
        import threading
        callback = lambda ch, method, properties, body: (
            self.lock.acquire(),
            self.local_task_queue.put(VideoTask.deserialize(json.loads(body.decode()))),
            self.lock.release(),
            time.sleep(3) if self.local_task_queue.qsize() >= 10 else None
            )
        self.subscriber.subscribe(callback)
        threading.Thread(target=self.subscriber.channel.start_consuming, daemon=True).start()

        while True:
            with self.lock:
                is_queue_empty = self.local_task_queue.empty()
            if not is_queue_empty:

                # task = self.get_task_from_incoming_mq()
                # print(task.get_seq_id())
                # print(task.get_source_id())
                # print(task.get_data())
                # continue

                task = self.get_task_from_incoming_mq()
                # print(task.get_seq_id())
                # print(task.get_source_id())
                # print(len(task.get_data()))
                # print(task.get_priority())
                print(f"Processing task {task.get_seq_id()} from source {task.get_source_id()}, task size: {len(task.get_data())}, priority: {task.get_priority()}")
                logging.info(f"Processing task {task.get_seq_id()} from source {task.get_source_id()}, task size: {len(task.get_data())}, priority: {task.get_priority()}")
                process_result = self.process_frames(self.decompress_frames(task.get_data()))
                # print(f"Processed result: {process_result}")
                # processed_task = VideoTask(process_result, task.get_seq_id(), task.get_source_id(), self.get_priority())

                # sleep_time = random.randint(1, 5)
                # print(f"Sleeping for {sleep_time} seconds")
                # time.sleep(sleep_time)

                # self.set_priority(self.get_priority_from_redis())
                print(f"Processor {self.get_id()} has priority {self.get_priority()}")
                processed_task = VideoTask(process_result, task.get_seq_id(), task.get_source_id(), self.get_priority())
                self.send_task_to_outgoing_mq(processed_task)
                
    
    def decompress_frames(self, compressed_video):
        video_data = base64.b64decode(compressed_video.encode('utf-8'))
        timestamp = time.time()
        temp_file_path = f'{timestamp}_temp_{self.get_id()}.mp4'
        with open(temp_file_path, 'wb') as f:
            f.write(video_data)
        frames = []
        cap = cv2.VideoCapture(temp_file_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        # Clean up temp file
        os.remove(temp_file_path)
        return frames

    def process_frames(self, frames):
        resized_frames = [self.resize_frame(frame, 160, 90) for frame in frames]
        compressed_video = self.compress_frames(resized_frames)
        base64_frame = base64.b64encode(compressed_video).decode('utf-8')
        grays = [self.compute_average_gray(frame) for frame in frames]
        average_grays = np.mean(grays)
        colors = [self.compute_average_color(frame) for frame in frames]
        average_colors = np.mean(colors, axis=0)

        
        return json.dumps({"average_grays": average_grays,
                           "average_colors": average_colors.tolist(),
                           "resized_frames": base64_frame})
    
    def compute_average_gray(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_gray = np.mean(gray)
        return average_gray
    
    def compute_average_color(self, frame):
        average_color_per_row = np.average(frame, axis=0)
        average_color = np.average(average_color_per_row, axis=0)
        return average_color
    
    def resize_frame(self, frame, width, height):
        resized_frame = cv2.resize(frame, (width, height))
        return resized_frame
    
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
    
    def get_priority_from_redis(self):
        p = self.redis_client.get(self.priority_redis_key)
        return int(p) if p else 10



if __name__ == '__main__':

                #  id: str, 
                #  incoming_mq_topic: str, 
                #  outgoing_mq_topic: str, 
                #  priority: int, 
                #  tuned_parameters: dict,
                #  tuned_parameters_redis_key: str,
                #  priority_redis_key: str,
                #  rabbitmq_host: str = 'localhost', 
                #  rabbitmq_port: int = 5672, 
                #  rabbitmq_username:str = 'guest', 
                #  rabbitmq_password: str = 'guest',
                #  rabbitmq_max_priority: int = 10,                 
                #  redis_host: str = 'localhost',
                #  redis_port: int = 6379,
                #  redis_db: int = 0):
    import os
    init_parameters = os.environ['INIT_PARAMETERS']
    id = os.environ['ID']
    incoming_mq_topic = os.environ['RABBIT_MQ_INCOMING_QUEUE']
    outgoing_mq_topic = os.environ['RABBIT_MQ_OUTGOING_QUEUE']
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

    processor = VideoProcessor1(id,
                                incoming_mq_topic,
                                outgoing_mq_topic,
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
    processor.run()



