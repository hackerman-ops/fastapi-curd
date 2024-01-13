from rabbitmq import RabbitMQ

mq_mapping = {"rabbitmq": RabbitMQ}


class MQ:
    def __init__(self, topic, mq_type="rabbit"):
        self.mq = mq_type
        self.topic = topic
        self.mq_class_instance = mq_mapping.get(mq_type, RabbitMQ)(self.topic)

    def send(self, data, delay=None):
        self.mq_class_instance.send(data, delay=delay)

    def get_consumer(self, callback):
        return self.mq_class_instance.get_consumer(callback=callback)


if __name__ == "__main__":
    data_ = {"delay": "I am trying delay"}
    MQ("hello").send(data_, delay=5000)
