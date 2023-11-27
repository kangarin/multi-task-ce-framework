# add base path to sys.path
import os, sys
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.aggregator import Aggregator
from framework.message_queue.mqtt import MqttSubscriber, MqttPublisher
import json
import threading

global aggregator

# flask part

from flask import Flask, jsonify
from flask_cors import CORS

Flask.logger_name = "listlogger"
app = Flask(__name__)
CORS(app)

@app.route('/result')
def result():
    with aggregator.lock:
        return jsonify(aggregator.result_window)

# end of flask part

if __name__ == '__main__':
    from video_task import VideoTask
else:
    from .video_task import VideoTask

class VideoAggregator(Aggregator):
    def __init__(self, id: str, incoming_mq_topic: str, tuned_parameters: dict = { 'window_size': 10 },
                 mqtt_host: str = 'localhost', mqtt_port: int = 1883, mqtt_username:str = 'admin', 
                 mqtt_password: str = 'admin'):
        super().__init__(id, incoming_mq_topic, tuned_parameters)
        mqtt_client_id=str(id)
        self.subscriber = MqttSubscriber(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id+"_subscriber")
        # This will be accessed by different threads, so we need to use a lock
        self.lock = threading.Lock()
        self.local_task_queue = []
        self.result_window = []
        self.window_size = tuned_parameters['window_size']

    @classmethod
    def aggregator_type(cls) -> str:
        return 'video'
    
    @classmethod
    def aggregator_description(cls) -> str:
        return 'Video aggregator'
    
    def get_id(self) -> str:
        return self._id
    
    def get_incoming_mq_topic(self) -> str:
        return self._incoming_mq_topic
    
    def get_tuned_parameters(self) -> dict:
        return self._tuned_parameters
    
    def set_tuned_parameters(self, tuned_parameters: dict):
        self._tuned_parameters = tuned_parameters

    def get_task_from_incoming_mq(self) -> VideoTask:
        with self.lock:
            return self.local_task_queue.pop(0)
    
    def get_latest_results(self) -> list:
        return self.result_window
    
    def run(self):
        self.subscriber.subscribe(self._incoming_mq_topic, 
                                  callback=(lambda client, userdata, message:(
                                      self.lock.acquire(), 
                                      self.local_task_queue.append(VideoTask.deserialize(json.loads(message.payload.decode()))), 
                                      self.lock.release())),
                                      qos=2                                     
                                  )
        self.subscriber.client.loop_start()

        # for testing
        output_frequency = 5

        while True:
            if len(self.local_task_queue) > 0:
                task = self.get_task_from_incoming_mq()
                print(f"Aggregating task {task.get_seq_id()} from source {task.get_source_id()}")
                with self.lock:
                    self.insert_result(task)
                # print(f"Aggregated task {task.get_seq_id()} from source {task.get_source_id()}")
                # for testing
                if task.get_seq_id() % output_frequency == 0:
                    print(f"Latest results: {self.result_window}")
                

    def insert_result(self, task: VideoTask):
        seq_id = task.get_seq_id()
        data = task.get_data()
        # insert the result into the result window in an ascending order of seq_id
        if len(self.result_window) == 0:
            self.result_window.append((seq_id, data))
        else:
            inserted = False
            for i in range(len(self.result_window)):
                # if duplicated, discard
                if seq_id == self.result_window[i][0]:
                    inserted = True
                    break
                elif seq_id < self.result_window[i][0]:
                    self.result_window.insert(i, (seq_id, data))
                    inserted = True
                    break
            if not inserted:
                self.result_window.append((seq_id, data))
        # if the result window is full, then remove the oldest result
        if len(self.result_window) > self.window_size:
            self.result_window.pop(0)
        print(f"Aggregated task {task.get_seq_id()} from source {task.get_source_id()}")


def start_flask(port=9856):
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    import os
    id = os.environ['REDIS_KEY'].split('_')[-1]
    port = int(os.environ['FLASK_PORT'])
    mqtt_incoming_topic = os.environ['MQTT_INCOMING_TOPIC']
    mqtt_broker_ip = os.environ['MQTT_BROKER_IP']
    mqtt_broker_port = int(os.environ['MQTT_BROKER_PORT'])
    print(id, mqtt_incoming_topic, mqtt_broker_ip, mqtt_broker_port)


    # mqtt_broker_ip = "172.27.155.106"
    # mqtt_broker_port = 1883
    # mqtt_incoming_topic = "$share/python/headup_detection/video_aggregator_1"
    # id = "1"
    # port = 9753

    # 启动flask服务
    flask_thread = threading.Thread(target=start_flask, args=(port,),daemon=True)
    flask_thread.start()

    aggregator = VideoAggregator(f'aggregator_{id}', mqtt_incoming_topic, { 'window_size': 8 }, mqtt_broker_ip, mqtt_broker_port)
    aggregator.run()