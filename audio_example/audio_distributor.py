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
    from audio_task import AudioTask
else:
    from .audio_task import AudioTask


# use regex to match and substitude the topic, key for matching and value for substituting
# for example, map 'generator_xxx' to 'aggregator_xxx'


class AudioDistributor(Distributor):
    def __init__(self, id: str, incoming_mq_topic: str,
                 mqtt_host: str = '138.3.208.203', mqtt_port: int = 1883,
                 mqtt_username: str = 'admin', mqtt_password: str = 'admin',
                 topic_mapping_rules={r'generator_(\w+)': r'testapp/aggregator_\1', }) -> None:
        super().__init__(id, incoming_mq_topic)
        mqtt_client_id = str(id)
        self.topic_mapping_rules = topic_mapping_rules
        self.subscriber = MqttSubscriber(mqtt_host, mqtt_port, mqtt_username, mqtt_password,
                                         mqtt_client_id + "_subscriber")
        self.publisher = MqttPublisher(mqtt_host, mqtt_port, mqtt_username, mqtt_password,
                                       mqtt_client_id + "_publisher")
        # This will be accessed by different threads, so we need to use a lock
        self.lock = threading.Lock()
        self.local_task_queue = []

    @classmethod
    def distributor_type(cls) -> str:
        return 'audio'

    @classmethod
    def distributor_description(cls) -> str:
        return 'Audio distributor'

    def get_id(self) -> str:
        return self._id

    def get_incoming_mq_topic(self) -> str:
        return self._incoming_mq_topic

    def get_task_from_incoming_mq(self) -> AudioTask:
        with self.lock:
            return self.local_task_queue.pop(0)

    def distribute_task_to_outgoing_mq_list(self, task: AudioTask):
        source_id = task.get_source_id()
        # parse source_id and find the corresponding outgoing_mq_topic by matching the topic_mapping_rules
        outgoing_mq_topic = None
        for rule in self.topic_mapping_rules:
            # if source_id matches certain pattern, then use the corresponding outgoing_mq_topic
            if re.match(rule, source_id):
                outgoing_mq_topic = re.sub(rule, self.topic_mapping_rules[rule], source_id)
                break
        if outgoing_mq_topic is not None:
            self.publisher.publish(outgoing_mq_topic, json.dumps(task.serialize()), qos=2)
            print(f"Distributed task {task.get_seq_id()} from source {task.get_source_id()} to {outgoing_mq_topic}")

    def run(self):
        self.subscriber.subscribe(self._incoming_mq_topic,
                                  callback=(lambda client, userdata, message: (
                                      self.lock.acquire(),
                                      self.local_task_queue.append(
                                          AudioTask.deserialize(json.loads(message.payload.decode()))),
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
                print(task.get_metadata())
                print(f"Distributing task {task.get_seq_id()} from source {task.get_source_id()}")
                self.distribute_task_to_outgoing_mq_list(task)


if __name__ == '__main__':
    # test
    import argparse

    parser = argparse.ArgumentParser(description='Audio distributor')
    parser.add_argument('--id', type=str, default=1, help='distributor id')
    id = parser.parse_args().id
    distributor = AudioDistributor(f'distributor_{id}', '$share/python/testapp/processor_stage_2')
    distributor.run()
