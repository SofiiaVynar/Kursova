from output_strategy import OutputStrategy
import redis
import json


class RedisOutput(OutputStrategy):
    def __init__(self, host='localhost', port=6379):
        self.client = redis.Redis(host=host, port=port)

    def output(self, data: dict):
        self.client.rpush("animal_data", json.dumps(data))
