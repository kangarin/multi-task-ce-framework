from paho.mqtt import client as mqtt_client

class MqttPublisher:
    def __init__(self, host, port, username, password, client_id):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id

        self.client = mqtt_client.Client(self.client_id)
        # self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.host, self.port)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def disconnect(self):
        self.client.disconnect()

class MqttSubscriber:
    def __init__(self, host, port, username, password, client_id):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id

        self.client = mqtt_client.Client(self.client_id)
        # self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.host, self.port)

    def subscribe(self, topic, callback):
        self.client.subscribe(topic)
        self.client.on_message = callback

    def disconnect(self):
        self.client.disconnect()

# test MqttPublisher and MqttSubscriber
if __name__ == '__main__':
    import time
    import json

    def on_message(client, userdata, message):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")

    # publisher = MqttPublisher('localhost', 1883, 'admin', 'admin', 'publisher')
    subscriber = MqttSubscriber('localhost', 1883, 'admin', 'admin', 'subscriber')

    subscriber.subscribe('/python/video', on_message)

    subscriber.client.loop_start()
    # publisher.client.loop_start()

    # publisher.publish('/python/test', json.dumps({'test': 'test'}))

    time.sleep(100)
    # publisher.disconnect()
    subscriber.disconnect()