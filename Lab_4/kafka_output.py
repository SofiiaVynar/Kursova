from kafka import KafkaProducer
from output_strategy import OutputStrategy

import json


class KafkaOutput(OutputStrategy):
    def __init__(self, topic="animal_topic", bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks=0
        )
        self.topic = topic

    def output(self, data: dict):
        self.producer.send(self.topic, data)
