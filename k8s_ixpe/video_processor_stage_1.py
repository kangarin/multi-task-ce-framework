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
import util_ixpe

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

        self.d_area = self.init_parameters['d_area']
        self.bar_area = self.init_parameters['bar_area'] 
        self.mat_detector = util_ixpe.MaterialDetection(
        detection_area=self.d_area, buffer_size=20)
        self.bar_selector = util_ixpe.BarSelection(bar_area=self.bar_area)
        self.first_done_flag = False

    @classmethod
    def processor_type(cls) -> str:
        return 'video'

    @classmethod
    def processor_description(cls) -> str:
        return 'ixpe preprocess'

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

                frames = self.decompress_frames(task.get_data())
                process_result = []
                for frame in frames:
                    result = self.process_frame(frame)
                    process_result.append(result)
                for output_ctx in process_result:
                    if "frame" in output_ctx:
                        output_ctx["frame"] = self.encode_image(output_ctx["frame"])
                    if "bar_roi" in output_ctx:
                        output_ctx["bar_roi"] = self.encode_image(output_ctx["bar_roi"])
                        # change a tuple of two numbers into a list of two numbers
                        output_ctx["abs_point"] = list(output_ctx["abs_point"])
                task_content = {
                    "result": process_result,
                    "data_source_redis_key": "ixpe_" + task.get_source_id()
                }
                # print(f"Processed result: {process_result}")
                # processed_task = VideoTask(process_result, task.get_seq_id(), task.get_source_id(), self.get_priority())

                # sleep_time = random.randint(1, 5)
                # print(f"Sleeping for {sleep_time} seconds")
                # time.sleep(sleep_time)

                # self.set_priority(self.get_priority_from_redis())
                print(f"Processor {self.get_id()} has priority {self.get_priority()}")
                processed_task = VideoTask(json.dumps(task_content), task.get_seq_id(), task.get_source_id(), self.get_priority())
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
    
    def process_frame(self, frame):
        output_ctx = {}
        if not self.mat_detector.detect(frame=frame):
            print('no material detected, continue')
            return output_ctx
        bar_roi, abs_point = self.bar_selector.select(frame=frame)
        if abs_point != (0, 0):
            if not self.first_done_flag:
                self.first_done_flag = True
                print('select bar roi success')
            output_ctx["bar_roi"] = bar_roi
            output_ctx["abs_point"] = abs_point
            output_ctx["frame"] = frame
        return output_ctx
     
    
    def get_priority_from_redis(self):
        p = self.redis_client.get(self.priority_redis_key)
        return int(p) if p else 10
    
    # def encode_image(self, img):
    #     # 编码图像
    #     _, encoded_img = cv2.imencode('.jpg', img)
    #     encoded_img_bytes = encoded_img.tobytes()
    #     return encoded_img_bytes
    
    # def decode_image(self, encoded_img_bytes):
    #     # 解码图像
    #     decoded_img = cv2.imdecode(np.frombuffer(encoded_img_bytes, np.uint8), cv2.IMREAD_COLOR)
    #     return decoded_img

    import base64

    def encode_image(self, img):
        # 编码图像
        _, encoded_img = cv2.imencode('.jpg', img)
        encoded_img_bytes = encoded_img.tobytes()
        # 转换为 Base64 编码的字符串
        encoded_img_str = base64.b64encode(encoded_img_bytes).decode('utf-8')
        return encoded_img_str
    
    def decode_image(self, encoded_img_str):
        # 将 Base64 编码的字符串转换回 bytes
        encoded_img_bytes = base64.b64decode(encoded_img_str)
        # 解码图像
        decoded_img = cv2.imdecode(np.frombuffer(encoded_img_bytes, np.uint8), cv2.IMREAD_COLOR)
        return decoded_img


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
    init_parameters = json.loads(os.environ['INIT_PARAMETERS'])
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

    processor = VideoProcessor1(
                                init_parameters,
                                id,
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



