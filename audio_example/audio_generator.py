# add base path to sys.path
import os, sys

print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.generator import Generator
from framework.message_queue.mqtt import MqttPublisher
import json
import time
import base64
import wave
import numpy as np

if __name__ == '__main__':
    from audio_task import AudioTask
else:
    from .audio_task import AudioTask


class AudioGenerator(Generator):
    def __init__(self, data_source, id, mq_topic, priority, tuned_parameters,
                 mqtt_host='138.3.208.203', mqtt_port=1883, mqtt_username='admin',
                 mqtt_password='admin'):
        super().__init__(data_source, id, mq_topic, priority, tuned_parameters)
        mqtt_client_id = str(id)
        self.publisher = MqttPublisher(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id)
        self._data_source = wave.open(data_source, "r")

    @classmethod
    def generator_type(cls) -> str:
        return 'audio'

    @classmethod
    def generator_description(cls) -> str:
        return 'Audio generator'

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

    def send_task_to_mq(self, task: AudioTask):
        # print(len(json.dumps(task.serialize())))
        self.publisher.publish(self._mq_topic, json.dumps(task.serialize()), qos=2)

    def run(self):
        self.publisher.client.loop_start()

        frames_per_task = self.get_tuned_parameters()['frames_per_task']
        mode = self.get_tuned_parameters()['mode']
        # temp_frame_buffer = []

        params = self._data_source.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        id = 0
        cnt = frames_per_task * framerate  # 4 * 8000
        while id * cnt < nframes:
            self._data_source.setpos(id * cnt)
            data = self._data_source.readframes(min(cnt, nframes - id * cnt))
            base64_data = base64.b64encode(data).decode('utf-8')

            self.get_tuned_parameters().update({'sampwidth': sampwidth, 'framerate': framerate})
            task = AudioTask(base64_data, id, self._id, self._priority, self.get_tuned_parameters())
            self.send_task_to_mq(task)
            print(f"Generated task {task.get_seq_id()} from source {task.get_source_id()}")
            id += 1
            # temp_frame_buffer = []
            time.sleep(5)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Audio generator')
    parser.add_argument('--id', type=str, default=1, help='generator id')
    id = parser.parse_args().id
    generator = AudioGenerator(r"drill_noise.wav", f'generator_{id}',
                               'testapp/generator', 0, {"frames_per_task": 4, "mode": 2})
    generator.run()
