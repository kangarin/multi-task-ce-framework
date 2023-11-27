# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from framework.service.distributor import Distributor
from framework.message_queue.mqtt import MqttSubscriber, MqttPublisher
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
                 mqtt_host: str = 'localhost', mqtt_port: int = 1883, 
                 mqtt_username:str = 'admin', mqtt_password: str = 'admin',
                 topic_mapping_rules = {r'generator': r'aggregator'}) -> None:
        super().__init__(id, incoming_mq_topic)
        mqtt_client_id=str(id)
        self.topic_mapping_rules = topic_mapping_rules
        self.subscriber = MqttSubscriber(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id+"_subscriber")
        self.publisher = MqttPublisher(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id+"_publisher")
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

        # self.incoming_mq_topic is like "$xxx/xxxxxx/headup_detection/video_processor_stage_2"
        # use "headup_detection/" as the prefix of outgoing_mq_topic, in another word, use the second last part of incoming_mq_topic as the prefix of outgoing_mq_topic
        # How to use slices to get the second last part of a string?

        outgoing_mq_topic = self._incoming_mq_topic.split('/')[-2] + '/' + source_id

        self.publisher.publish(outgoing_mq_topic, json.dumps(task.serialize()), qos=2)
        print(f"Distributed task {task.get_seq_id()} from source {task.get_source_id()} to {outgoing_mq_topic}")
        

    def run(self):
        self.subscriber.subscribe(self._incoming_mq_topic, 
                                  callback=(lambda client, userdata, message:(
                                      self.lock.acquire(), 
                                      self.local_task_queue.append(VideoTask.deserialize(json.loads(message.payload.decode()))), 
                                      self.lock.release())),
                                      qos=2                                     
                                  )
        self.subscriber.client.loop_start()
        self.publisher.client.loop_start()
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

    import os
    id = os.environ['REDIS_KEY'].split('_')[-1]
    mqtt_broker_ip = os.environ['MQTT_BROKER_IP']
    mqtt_broker_port = int(os.environ['MQTT_BROKER_PORT'])
    mqtt_incoming_topic = os.environ['MQTT_INCOMING_TOPIC']

    # mqtt_broker_ip = "172.27.155.106"
    # mqtt_broker_port = 1883
    # mqtt_incoming_topic = "$share/python/headup_detection/video_processor_stage_2"
    # id = "1"

    print(id, mqtt_broker_ip, mqtt_broker_port, mqtt_incoming_topic)
    distributor = VideoDistributor(f'distributor_instance_{id}', mqtt_incoming_topic, mqtt_broker_ip, mqtt_broker_port)
    distributor.run()