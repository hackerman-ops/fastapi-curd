from rabbitmq import RabbitMQ

mq_mapping = {"rabbitmq": RabbitMQ}


class MQ:
    def __init__(self, topic, mq_type="rabbit"):
        self.mq = mq_type
        self.topic = topic
        self.mq_class_instance = mq_mapping.get(mq_type, RabbitMQ)(self.topic)

    def send(self, data):
        self.mq_class_instance.send(data)

    def get_consumer(self, callback):
        return self.mq_class_instance.get_consumer(callback=callback)


if __name__ == "__main__":

    def _callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 发送ack消息

    consumer = MQ("hello").get_consumer(callback=_callback)
    consumer.start_consuming()
