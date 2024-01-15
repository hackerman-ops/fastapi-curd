from utils.mq_option.rabbitmq import RabbitMQ

mq_mapping = {"rabbitmq": RabbitMQ}
import logging

logger = logging.get_logger(__name__)


class MQ:
    def __init__(self, topic, mq_type="rabbit"):
        self.mq = mq_type
        self.topic = topic
        self.mq_class_instance = mq_mapping.get(mq_type, RabbitMQ)(self.topic)

    def send(self, data):
        self.mq_class_instance.send(data)

    def get_consumer(self, callback):
        return self.mq_class_instance.get_consumer(callback=callback)


def consume_with_killer(topic, tag, callback):
    """
    app: 业务类

    """

    mq_instance = MQ(topic)
    consumer = mq_instance.get_consumer(callback)
    try:
        # 长轮询消费消息
        consumer.start_consuming()

    except Exception as e:
        logger.error(f"{tag}出现异常")
