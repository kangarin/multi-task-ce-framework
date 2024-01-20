# add base path to sys.path
import os, sys

print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from framework.service.generator import Generator
from framework.message_queue.mqtt import MqttPublisher
import json
import base64
import time
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

if __name__ == '__main__':
    from imu_task import ImuTask
else:
    from .imu_task import ImuTask


class ImuGenerator(Generator):
    def __init__(self, data_source: object,
                 id: str,
                 mq_topic: str,
                 priority: int,
                 tuned_parameters: dict,
                 mqtt_host: str = 'localhost',
                 mqtt_port: int = 1883,
                 mqtt_username: str = 'admin',
                 mqtt_password: str = 'admin'):
        super().__init__(data_source, id, mq_topic, priority, tuned_parameters)
        mqtt_client_id = str(id)
        self.publisher = MqttPublisher(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_client_id)
        # self._data_source = pd.read_csv(data_source)
        self._data_source = data_source

    @classmethod
    def generator_type(cls) -> str:
        return 'imu'

    @classmethod
    def generator_description(cls) -> str:
        return 'Imu generator'

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

    def send_task_to_mq(self, task: ImuTask):
        # print(len(json.dumps(task.serialize())))
        self.publisher.publish(self._mq_topic, json.dumps(task.serialize()), qos=2)

    def run(self):
        self.publisher.client.loop_start()
        id = 0
        folder_path=self._data_source
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)
                csv_data = pd.read_csv(file_path)
                print(file_path)
                start_id, end_id = self.end_point_detection(csv_data)
                num_bin = len(start_id)
                for bi in range(num_bin):
                    start_idx = int(start_id[bi])
                    end_idx = int(end_id[bi]) + 1
                    data = csv_data.iloc[start_idx:end_idx, [1, 6, 7, 8, 19, 20, 21]].values
                    data = np.ascontiguousarray(data)
                    byte_data=data.tobytes()
                    base64_frame = (base64.b64encode(byte_data)).decode('utf-8')
                    decoded_data = np.frombuffer(base64.b64decode(base64_frame.encode('utf-8'))).reshape(data.shape)
                    task = ImuTask(base64_frame, id, self._id, self._priority, self.get_tuned_parameters())
                    self.send_task_to_mq(task)
                    print(f"Generated task {task.get_seq_id()} from source {task.get_source_id()}")
                    id += 1
                    time.sleep(5)

    def end_point_detection(self,csv_data):
        linear_acceleration = csv_data.iloc[:, 19:22].values
        angular_velocity = csv_data.iloc[:, 6:9].values
        timestamp = csv_data.iloc[:, 1:2].values
        # transform unit
        # gyro : from deg to rad
        angular_velocity = angular_velocity / 180 * np.pi
        # linearacc: from g to m/s/s
        linear_acceleration = linear_acceleration * 9.81
        start_id, end_id = self.extractMotionLPMS3(timestamp, angular_velocity, linear_acceleration, 2)
        return start_id, end_id

    def extractMotionLPMS3(self, lpms_time, lpms_gyro, lpms_linearacc, thre):
        x1 = np.sqrt(np.sum(lpms_linearacc ** 2, axis=1))
        x2 = np.sqrt(np.sum(lpms_gyro ** 2, axis=1))
        x = x1 + 5 * x2
        wlen = 10
        inc = 5
        win = np.hanning(wlen + 2)[1:-1]
        X = self.enframe(x, win, inc)
        X = np.transpose(X)
        fn = X.shape[1]
        time = lpms_time
        id = np.arange(wlen / 2, wlen / 2 + (fn - 1) * inc + 1, inc)
        id = id - 1
        frametime = time[id.astype(int)]
        En = np.zeros(fn)

        for i in range(fn):
            u = X[:, i]
            u2 = u * u
            En[i] = np.sum(u2)
        locs, pks = find_peaks(En, height=max(En) / 20, distance=15)
        pks = pks['peak_heights']
        # initialize startend_locs
        startend_locs = np.zeros((len(locs), 2), dtype=int)
        for i in range(len(locs)):
            si = locs[i] - 1
            while si > 0:
                if En[si] < thre:
                    break
                si -= 1

            ei = locs[i] + 1
            while ei < len(En):
                if En[ei] < thre:
                    break
                ei += 1

            startend_locs[i, 0] = si
            startend_locs[i, 1] = ei

        # delete repeat points
        startend_locs = np.unique(startend_locs, axis=0)

        # get id range
        start_id = id[startend_locs[:, 0]]
        end_id = id[startend_locs[:, 1] - 1]
        return start_id, end_id

    def enframe(self, x, win, inc):
        nx = len(x)
        nwin = len(win)
        if nwin == 1:
            length = win
        else:
            length = nwin
        nf = int(np.fix((nx - length + inc) / inc))
        f = np.zeros((nf, length))
        indf = inc * np.arange(nf).reshape(-1, 1)
        inds = np.arange(1, length + 1)
        f[:] = x[indf + inds - 1]  # 对数据分帧
        if nwin > 1:
            w = win.ravel()
            f = f * w[np.newaxis, :]
        return f


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Imu generator')
    parser.add_argument('--id', type=str, help='generator id')
    parser.add_argument('--data_source', type=str, help='data source')
    id = parser.parse_args().id
    # data_source = parser.parse_args().data_source

    generator = ImuGenerator(r'E:\College\NJU\videoStable\6-axis', f'generator_{id}',
                             'testapp/generator', 0, {})
    generator.run()
