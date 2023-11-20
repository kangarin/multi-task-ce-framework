import pika

def get_channel(queue_name='priority-queue', max_priority=10, 
                host='localhost', port=5672, 
                username='guest', password='guest'):
    # 连接RabbitMQ并获取频道
    parameters = pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username=username, password=password))
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # 创建队列，设置最大优先级
    channel.queue_declare(
        queue=queue_name, arguments={"x-max-priority": max_priority}
    )
    return channel

class RabbitmqPublisher:
    def __init__(self, host, port, username, password, queue_name, max_priority):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.max_priority = max_priority

        self.channel = get_channel(queue_name, max_priority, host, port, username, password)

    def publish(self, payload, priority):
        self.channel.basic_publish(
            exchange='', routing_key=self.queue_name, body=payload,
            properties=pika.BasicProperties(delivery_mode=2, priority=priority)
        )

    def disconnect(self):
        self.channel.close()

class RabbitmqSubscriber:
    def __init__(self, host, port, username, password, queue_name, max_priority):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.max_priority = max_priority

        self.channel = get_channel(queue_name, max_priority, host, port, username, password)

    def subscribe(self, callback):
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=callback, auto_ack=True
        )

    def disconnect(self):
        self.channel.close()

if __name__ == '__main__':
    # parse args, 0 for publisher, 1 for subscriber
    import argparse
    parser = argparse.ArgumentParser(description='RabbitMQ publisher/subscriber')
    parser.add_argument('--type', type=int, help='0 for publisher, 1 for subscriber')

    args = parser.parse_args()

    if args.type == 0:
        # publisher
        publisher = RabbitmqPublisher('localhost', 5672, 'guest', 'guest', 'priority-queue', 10)

        for i in range(10):
            publisher.publish(str(i), i)

        publisher.disconnect()

    elif args.type == 1:
        # subscriber
        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)

        subscriber = RabbitmqSubscriber('localhost', 5672, 'guest', 'guest', 'priority-queue', 10)
        subscriber.subscribe(callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        subscriber.channel.start_consuming()

        subscriber.disconnect()