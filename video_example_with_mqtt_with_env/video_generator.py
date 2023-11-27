# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from framework.service.generator import Generator
import cv2
from framework.message_queue.mqtt import MqttPublisher
import json
import base64
import time

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoGenerator(Generator):
    def __init__(self, data_source: object, 
                 id: str, 
                 mq_topic: str, 
                 priority: int,
                 tuned_parameters: dict,
                 mqtt_host: str ='localhost', 
                 mqtt_port: int =1883, 
                 mqtt_username: str ='admin', 
                 mqtt_password: str ='admin'):
        super().__init__(data_source, id, mq_topic, priority, tuned_parameters)
        mqtt_client_id=str(id)
        self.publisher = MqttPublisher(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id)
        self._data_source = cv2.VideoCapture(data_source)

    @classmethod
    def generator_type(cls) -> str:
        return 'video'

    @classmethod
    def generator_description(cls) -> str:
        return 'Video generator'

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
        self.publisher.publish(self._mq_topic, json.dumps(task.serialize()), qos=2)

    def run(self):
        # import random
        # while True:
        #     random_num = random.randint(0, 100)
        #     yield random_num
        self.publisher.client.loop_start()
        id = 0
        cnt = 0
        
        frames_per_task = self.get_tuned_parameters()['frames_per_task']
        skipping_frame_interval = self.get_tuned_parameters()['skipping_frame_interval']
        temp_frame_buffer = []
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
                task = VideoTask(base64_frame, id, self._id, self._priority, self.get_tuned_parameters())
                self.send_task_to_mq(task)
                print(f"Generated task {task.get_seq_id()} from source {task.get_source_id()}")
                id += 1
                temp_frame_buffer = []
                time.sleep(5)


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
        out = cv2.VideoWriter(f'temp_{self.get_id()}.mp4', fourcc, 30, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()
        with open(f'temp_{self.get_id()}.mp4', 'rb') as f:
            compressed_video = f.read()
        # delete the temporary file
        os.remove(f'temp_{self.get_id()}.mp4')
        return compressed_video


if __name__ == '__main__':

    import os
    data_source = os.environ['DATA_SOURCE']
    mqtt_broker_ip = os.environ['MQTT_BROKER_IP']
    mqtt_broker_port = int(os.environ['MQTT_BROKER_PORT'])
    mqtt_topic = os.environ['MQTT_TOPIC']
    id = os.environ['REDIS_KEY'].split('_')[-1]

    # data_source = "rtsp://172.27.155.106:8554/mystream"
    # mqtt_broker_ip = "172.27.155.106"
    # mqtt_broker_port = 1883
    # mqtt_topic = "headup_detection/video_generator"
    # id = "1"
    
    print(data_source, mqtt_broker_ip, mqtt_broker_port, mqtt_topic, id)

    generator = VideoGenerator(data_source, f'video_generator_{id}',
                                 mqtt_topic, 0, {"frames_per_task": 5, "skipping_frame_interval": 5},
                                 mqtt_broker_ip, mqtt_broker_port)
    generator.run()

