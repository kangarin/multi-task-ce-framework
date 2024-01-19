# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.processor import Processor
from framework.message_queue.rabbitmq import RabbitmqPublisher, RabbitmqSubscriber
import json
import logging
import time
import threading
import base64
import cv2
import numpy as np
import random
from queue import PriorityQueue as PQ

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoProcessor2(Processor):
    def __init__(self, id: str, incoming_mq_topic: str, outgoing_mq_topic: str, 
                 priority: int, tuned_parameters: dict,
                 rabbitmq_host: str = 'localhost', rabbitmq_port: int = 5672, 
                 rabbitmq_username:str = 'guest', rabbitmq_password: str = 'guest',
                 rabbitmq_max_priority: int = 10):
        super().__init__(id, incoming_mq_topic, outgoing_mq_topic, priority, tuned_parameters)
        mqtt_client_id=str(id)
        self.subscriber = RabbitmqSubscriber(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, incoming_mq_topic, rabbitmq_max_priority)
        self.publisher = RabbitmqPublisher(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, outgoing_mq_topic, rabbitmq_max_priority)
        # This will be accessed by different threads, so we need to use a lock
        self.lock = threading.Lock()
        self.local_task_queue = PQ()

    @classmethod
    def processor_type(cls) -> str:
        return 'video'

    @classmethod
    def processor_description(cls) -> str:
        return 'Video processor2'

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
            if not self.local_task_queue.empty():
                task = self.get_task_from_incoming_mq()
                # print(task.get_seq_id())
                # print(task.get_source_id())
                # print(task.get_data())
                # print(task.get_priority())
                print(f"Processing task {task.get_seq_id()} from source {task.get_source_id()}, task size: {len(task.get_data())}, priority: {task.get_priority()}")
                task_data = json.loads(task.get_data())
                task_result = {}
                task_result["average_grays"] = task_data["average_grays"]
                task_result["average_colors"] = task_data["average_colors"]
                process_result = self.process_frames(self.decompress_frames(task_data["resized_frames"]))
                task_result["motion_level"] = process_result

                # sleep_time = random.randint(1, 5)
                # print(f"Sleeping for {sleep_time} seconds")
                # time.sleep(sleep_time)

                # processed_task = VideoTask(json.dumps(task_result), task.get_seq_id(), task.get_source_id(), self.get_priority())
                processed_task = VideoTask(json.dumps(task_result), task.get_seq_id(), task.get_source_id(), task.get_priority())
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

    def process_frames(self, frames):
        # calculate the difference between each frame and the next frame
        diff_frames = []
        for i in range(len(frames)-1):
            diff_frames.append(cv2.absdiff(frames[i], frames[i+1]))
        # calculate the average difference
        avg_diff = np.mean(diff_frames)
        return avg_diff
        # quantify the difference level
        if avg_diff <= 10:
            return "No motion"
        elif avg_diff <= 20:
            return "Low motion"
        elif avg_diff <= 30:
            return "Medium motion"
        else:
            return "High motion"











        


if __name__ == '__main__':
    # parse args from cmd
    import argparse
    parser = argparse.ArgumentParser(description='Video processor')
    parser.add_argument('--id', type=str, help='processor id')
    # parser.add_argument('--incoming_mq_topic', type=str, help='incoming message queue topic')
    # parser.add_argument('--outgoing_mq_topic', type=str, help='outgoing message queue topic')
    # parser.add_argument('--priority', type=int, help='processor priority')
    # parser.add_argument('--tuned_parameters', type=str, help='processor tuned parameters')
    args = parser.parse_args()
    id = args.id
    processor = VideoProcessor2(f'video_processor_stage_2_instance_{id}', 'testapp/video_processor_stage_1', 'testapp/video_processor_stage_2', 0, {})
    processor.run()



