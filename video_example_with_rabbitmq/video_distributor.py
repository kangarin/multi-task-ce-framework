# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from framework.service.distributor import Distributor
from framework.message_queue.rabbitmq import RabbitmqPublisher, RabbitmqSubscriber
import json
import re
import threading

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

# use regex to match and substitude the topic, key for matching and value for substituting
# for example, map 'generator_xxx' to 'aggregator_xxx'


class VideoDistributor(Distributor):
    def __init__(self, id: str, incoming_mq_topic: str,  
                 rabbitmq_host: str = 'localhost', rabbitmq_port: int = 5672, 
                 rabbitmq_username:str = 'guest', rabbitmq_password: str = 'guest',
                 rabbitmq_max_priority: int = 10,
                 topic_mapping_rules = {r'generator': r'aggregator'}) -> None:
        super().__init__(id, incoming_mq_topic)
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_username = rabbitmq_username
        self.rabbitmq_password = rabbitmq_password
        self.rabbitmq_max_priority = rabbitmq_max_priority
        self.topic_mapping_rules = topic_mapping_rules
        self.subscriber = RabbitmqSubscriber(rabbitmq_host, rabbitmq_port, rabbitmq_username, rabbitmq_password, incoming_mq_topic, rabbitmq_max_priority)
        # This will be accessed by different threads, so we need to use a lock
        self.lock = threading.Lock()
        self.local_task_queue = []

    @classmethod
    def distributor_type(cls) -> str:
        return 'video'

    @classmethod
    def distributor_description(cls) -> str:
        return 'Video distributor'

    def get_id(self) -> str:
        return self._id
    
    def get_incoming_mq_topic(self) -> str:
        return self._incoming_mq_topic
    
    def get_task_from_incoming_mq(self) -> VideoTask:
        with self.lock:
            return self.local_task_queue.pop(0)

    def distribute_task_to_outgoing_mq_list(self, task: VideoTask):
        source_id = task.get_source_id()
        # substitute the source_id with the topic_mapping_rules
        for key, value in self.topic_mapping_rules.items():
            source_id = re.sub(key, value, source_id)

        outgoing_mq_topic = self._incoming_mq_topic.split('/')[-2] + '/' + source_id
        self.publisher = RabbitmqPublisher(self.rabbitmq_host, self.rabbitmq_port, self.rabbitmq_username, self.rabbitmq_password, outgoing_mq_topic, self.rabbitmq_max_priority)
        self.publisher.publish(json.dumps(task.serialize()), task.get_priority())
        print(f"Distributed task {task.get_seq_id()} from source {task.get_source_id()} to {outgoing_mq_topic}, priority {task.get_priority()}")
         

    def run(self):
        import threading
        callback = lambda ch, method, properties, body: (
            self.lock.acquire(), 
            self.local_task_queue.append(VideoTask.deserialize(json.loads(body.decode()))), 
            self.lock.release())
        self.subscriber.subscribe(callback)
        threading.Thread(target=self.subscriber.channel.start_consuming, daemon=True).start()

        while True:
            if len(self.local_task_queue) > 0:
                task = self.get_task_from_incoming_mq()
                print(task.get_seq_id())
                print(task.get_source_id())
                print(task.get_data())
                print(task.get_priority())
                print(f"Distributing task {task.get_seq_id()} from source {task.get_source_id()}")
                self.distribute_task_to_outgoing_mq_list(task)

if __name__ == '__main__':
    # test
    import argparse
    parser = argparse.ArgumentParser(description='Video distributor')
    parser.add_argument('--id', type=str, help='distributor id')
    id = parser.parse_args().id
    distributor = VideoDistributor(f'video_distributor_{id}', 'testapp/video_processor_stage_2')
    distributor.run()