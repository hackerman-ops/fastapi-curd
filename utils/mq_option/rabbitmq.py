import json

import pika


def _callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # 发送ack消息


class RabbitMQ:
    def __init__(self, topic):
        self.topic = topic
        url = "amqp://yiyun:yiyun@localhost:5672/"
        parameters = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(parameters)

    def send(self, data, delay=None):
        properties = pika.BasicProperties(content_type="application/json")
        if delay:
            headers = {"x-delay": delay}
            properties.headers = headers
        channel = self.connection.channel()
        args = {"x-delayed-type": "direct"}
        channel.exchange_declare(
            exchange="delay-exchange",
            passive=True,
            exchange_type="x-delayed-message",
            arguments=args,
        )
        channel.queue_declare(queue=self.topic)
        channel.basic_publish(
            exchange="delay-exchange",
            routing_key=self.topic,
            body=json.dumps(data, ensure_ascii=False),
            properties=properties,
        )
        self.connection.close()

    def get_consumer(self, callback):
        channel = self.connection.channel()
        args = {"x-delayed-type": "direct"}
        channel.exchange_declare(
            exchange="delay-exchange",
            passive=True,
            exchange_type="x-delayed-message",
            arguments=args,
        )
        channel.queue_declare(queue=self.topic)
        channel.basic_consume(queue=self.topic, on_message_callback=callback)
        return channel
