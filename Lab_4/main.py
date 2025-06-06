import json
from console_output import ConsoleOutput
from kafka_output import KafkaOutput
from redis_output import RedisOutput
from web_reader import read_web_data


def get_strategy(strategy_name: str):
    if strategy_name == "console":
        return ConsoleOutput()
    elif strategy_name == "kafka":
        return KafkaOutput()
    elif strategy_name == "redis":
        return RedisOutput()
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")


if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    strategy = get_strategy(config["output_strategy"])
    url = "https://www.dallasopendata.com/resource/7h2m-3um5.json"

    for row in read_web_data(url):
        strategy.output(row)
