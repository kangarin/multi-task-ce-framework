# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.processor import Processor
from framework.message_queue.mqtt import MqttSubscriber, MqttPublisher
import json
import logging
import time
import cv2
import base64
import numpy as np

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoProcessor1(Processor):
    def __init__(self, id: str, incoming_mq_topic: str, outgoing_mq_topic: str, 
                 priority: int, tuned_parameters: dict,
                 mqtt_host: str = 'localhost', mqtt_port: int = 1883, mqtt_username:str = 'admin', 
                 mqtt_password: str = 'admin'):
        super().__init__(id, incoming_mq_topic, outgoing_mq_topic, priority, tuned_parameters)
        mqtt_client_id=str(id)
        self.subscriber = MqttSubscriber(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id+"_subscriber")
        self.publisher = MqttPublisher(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id+"_publisher")
        self.local_task_queue = []

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
        return self.local_task_queue.pop(0)

    def send_task_to_outgoing_mq(self, task: VideoTask):
        self.publisher.publish(self._outgoing_mq_topic, json.dumps(task.serialize()))

    def run(self):
        self.subscriber.subscribe(self._incoming_mq_topic, 
                                  callback=(lambda client, userdata, message:
                                        self.local_task_queue.append(VideoTask.deserialize(
                                            json.loads(message.payload.decode())
                                            )))
        )
        self.subscriber.client.loop_start()
        self.publisher.client.loop_start()
        while True:
            if len(self.local_task_queue) > 0:

                # task = self.get_task_from_incoming_mq()
                # print(task.get_seq_id())
                # print(task.get_source_id())
                # print(task.get_data())
                # continue


                task = self.get_task_from_incoming_mq()
                print(task.get_seq_id())
                print(task.get_source_id())
                print(len(task.get_data()))
                print(task.get_priority())
                print(f"Processing task {task.get_seq_id()} from source {task.get_source_id()}")
                process_result = self.process_frames(self.decompress_frames(task.get_data()))
                print(f"Processed result: {process_result}")
                processed_task = VideoTask(process_result, task.get_seq_id(), task.get_source_id(), self.get_priority())
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
        grays = [self.compute_average_gray(frame) for frame in frames]
        average_grays = np.mean(grays)
        return average_grays
    
    def compute_average_gray(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        average_gray = np.mean(gray)
        return average_gray


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
    processor = VideoProcessor1(f'processor_stage_1_instance_{id}', '$share/python/testapp/generator', 'testapp/processor_stage_1', 0, {})
    processor.run()



