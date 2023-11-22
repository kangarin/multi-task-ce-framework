# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.processor import Processor
from framework.message_queue.rabbitmq import RabbitmqPublisher, RabbitmqSubscriber
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

        args = {
            'net_type': 'mb_tiny_RFB_fd',
            'input_size': 480,
            'threshold': 0.7,
            'candidate_size': 1500,
            'device': 'cpu'
            # 'device': 'cuda:0'
        }

        if __name__ == '__main__':
            from headup_test.face_detection import FaceDetection
        else:
            from .headup_test.face_detection import FaceDetection
        detector = FaceDetection(args)

        while True:
            if not self.local_task_queue.empty():

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
                frames = self.decompress_frames(task.get_data())
                process_result = self.process_frames(frames, detector, task.get_seq_id())
                # print(f"Processed result: {process_result}")
                # processed_task = VideoTask(process_result, task.get_seq_id(), task.get_source_id(), self.get_priority())

                # sleep_time = random.randint(1, 5)
                # print(f"Sleeping for {sleep_time} seconds")
                # time.sleep(sleep_time)

                processed_task = VideoTask(process_result, task.get_seq_id(), task.get_source_id(), task.get_priority())
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

    def process_frames(self, frames, detector, task_id):
        results = []
        frame_cnt = 1
        for frame in frames:
            input_ctx = {}
            input_ctx['image'] = frame
            result = detector(input_ctx)
            if "faces" in result:
                for i in range(len(result["faces"])):
                    face = result["faces"][i]
                    result["faces"][i] = encode_image(face)

            result['frame_id'] = str(task_id) + '_' + str(frame_cnt)
            # print(result)
            results.append(result)
            frame_cnt += 1

        
        return json.dumps(results)
    
def encode_image(img_rgb):
    img_bytestr = str(cv2.imencode('.jpg', img_rgb)[1].tobytes())

    return img_bytestr

def decode_image(img_bytes):
    img_jpg = np.frombuffer(eval(img_bytes), dtype=np.uint8)
    img_rgb = np.array(cv2.imdecode(img_jpg, cv2.IMREAD_UNCHANGED))

    return img_rgb



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
    processor = VideoProcessor1(f'processor_stage_1_instance_{id}', 'testapp/generator', 'testapp/processor_stage_1', 0, {})
    processor.run()



