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
import threading
import base64
import cv2
import numpy as np
import random
from queue import PriorityQueue as PQ
import util_ixpe

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoProcessor2(Processor):
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
        self.redis_priority_key = id
        self.tuned_parameters_redis_key = tuned_parameters_redis_key
        self.priority_redis_key = priority_redis_key
        self.sr_generator = util_ixpe.ESCPN()

    @classmethod
    def processor_type(cls) -> str:
        return 'video'

    @classmethod
    def processor_description(cls) -> str:
        return 'ixpe generate super resolution'

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
                task = self.get_task_from_incoming_mq()
                # print(task.get_seq_id())
                # print(task.get_source_id())
                # print(task.get_data())
                # print(task.get_priority())
                print(f"Processing task {task.get_seq_id()} from source {task.get_source_id()}, task size: {len(task.get_data())}, priority: {task.get_priority()}")
                logging.info(f"Processing task {task.get_seq_id()} from source {task.get_source_id()}, task size: {len(task.get_data())}, priority: {task.get_priority()}")

                task_data_raw = task.get_data()
                # print(task_data_raw)
                if isinstance(task_data_raw, str):
                    task_data_raw = json.loads(task_data_raw)
                task_data = task_data_raw["result"]
                data_source_redis_key =  task_data_raw["data_source_redis_key"]
                process_result = []
                for input_ctx in task_data:
                    if "frame" in input_ctx:
                        input_ctx["frame"] = self.decode_image(input_ctx["frame"])
                    if "bar_roi" in input_ctx:
                        input_ctx["bar_roi"] = self.decode_image(input_ctx["bar_roi"])
                    if "abs_point" in input_ctx:
                        # change a list of two numbers into a tuple of two numbers
                        input_ctx["abs_point"] = tuple(input_ctx["abs_point"])

                    output_ctx = self.process_task(input_ctx, data_source_redis_key)

                    if "frame" in output_ctx:
                        output_ctx["frame"] = self.encode_image(output_ctx["frame"])
                    if "bar_roi" in output_ctx:
                        output_ctx["bar_roi"] = self.encode_image(output_ctx["bar_roi"])
                    if "abs_point" in output_ctx:
                        # change a tuple of two numbers into a list of two numbers
                        output_ctx["abs_point"] = list(output_ctx["abs_point"])
                    if "srl" in output_ctx:
                        output_ctx["srl"] = self.encode_image(output_ctx["srl"])
                    if "srr" in output_ctx:
                        output_ctx["srr"] = self.encode_image(output_ctx["srr"])
                    if "labs_point" in output_ctx:
                        # change a tuple of two numbers into a list of two numbers
                        output_ctx["labs_point"] = list(output_ctx["labs_point"])
                    if "rabs_point" in output_ctx:
                        # change a tuple of two numbers into a list of two numbers
                        output_ctx["rabs_point"] = list(output_ctx["rabs_point"])

                    process_result.append(output_ctx)

                task_content = {
                    "result": process_result,
                    "data_source_redis_key": "ixpe_" + task.get_source_id()
                }
                # sleep_time = random.randint(1, 5)
                # print(f"Sleeping for {sleep_time} seconds")
                # time.sleep(sleep_time)

                # processed_task = VideoTask(json.dumps(task_result), task.get_seq_id(), task.get_source_id(), self.get_priority())
                # self.set_priority(self.get_priority_from_redis())
                print(f"Processor {self.get_id()} has priority {self.get_priority()}")

                # print("Type of task_content is: "+ type(task_content))
                # print("Type of result is: " + type(task_content["result"]))

                processed_task = VideoTask(json.dumps(task_content), task.get_seq_id(), task.get_source_id(), self.get_priority())
                self.send_task_to_outgoing_mq(processed_task)
                
    def decompress_frames(self, compressed_video):
        video_data = base64.b64decode(compressed_video.encode('utf-8'))
        temp_file_path = f'temp_{self.get_id()}.mp4'
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


    # input_ctx is json from the following code:
    # output_ctx["bar_roi"] = bar_roi
    # output_ctx["abs_point"] = abs_point
    # output_ctx["frame"] = frame
    # result.append(output_ctx)
    def process_task(self, input_ctx, data_source_redis_key):
        output_ctx = {}
        # if input_ctx does not contain 'frame'
        if 'frame' not in input_ctx:
            # case 1: return empty due to no input_ctx
            print("case 1: return empty due to no input_ctx")
            return output_ctx
        bar_roi, abs_point, frame = input_ctx["bar_roi"], input_ctx["abs_point"], input_ctx["frame"]
        abs_point = tuple(abs_point)
        lps, rps = self.get_edge_position_from_redis(data_source_redis_key)
        print(f"lps: {lps}, rps: {rps}")
        
        if lps == 0 and rps == 0:
            output_ctx["bar_roi"] = bar_roi
            output_ctx["abs_point"] = abs_point
            output_ctx["frame"] = frame
            # case 2: return 3 parameters
            print("case 2: return 3 parameters")
            return output_ctx
        else:
            lroi, rroi, p1, p3 = self.extractMinimizedROI(
                bar_roi, lps, rps, abs_point)
            if lroi.size == 0 or rroi.size == 0:
                # case 3: return empty
                print("case 3: return empty")
                return output_ctx
            else:
                srl = self.sr_generator.genSR(lroi)
                srr = self.sr_generator.genSR(rroi)

                labs_point = (abs_point[0] + p1[0], abs_point[1] + p1[1])
                rabs_point = (abs_point[0] + p3[0], abs_point[1] + p3[1])
                output_ctx["srl"] = srl
                output_ctx["srr"] = srr
                output_ctx["labs_point"] = labs_point
                output_ctx["rabs_point"] = rabs_point
                output_ctx["frame"] = frame
                # case 4: return 5 parameters
                print("case 4: return 5 parameters")
                return output_ctx

    def get_priority_from_redis(self):
        p = self.redis_client.get(self.redis_priority_key) 
        return int(p) if p else 10    
    
    def extractMinimizedROI(self, bar_roi, lps, rps, abs_point):
        lps = int(lps - abs_point[0])
        rps = int(rps - abs_point[0])
        sliding_threshold = 10
        hl_threshold = 15
        height = bar_roi.shape[0]
        p1 = (lps - 3 * hl_threshold - sliding_threshold, 0)
        p2 = (lps + hl_threshold + sliding_threshold, height)
        p3 = (rps - hl_threshold - sliding_threshold, 0)
        p4 = (rps + 3 * hl_threshold + sliding_threshold, height)
        lroi = bar_roi[p1[1]:p2[1], p1[0]:p2[0]]
        rroi = bar_roi[p3[1]:p4[1], p3[0]:p4[0]]
        return lroi, rroi, p1, p3
    
    def get_edge_position_from_redis(self, data_source_redis_key):
        lps_key = f"{data_source_redis_key}_lps"
        rps_key = f"{data_source_redis_key}_rps"
        lps = self.redis_client.get(lps_key)
        rps = self.redis_client.get(rps_key)
        return int(lps) if lps else 0, int(rps) if rps else 0
    
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

    processor = VideoProcessor2(
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