import csv
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


def write_to_csv(data_iterable, file_path: str):
    data_list = list(data_iterable)

    fieldnames = set()
    for item in data_list:
        fieldnames.update(item.keys())
    fieldnames = list(fieldnames)

    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)


if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    strategy = get_strategy(config["output_strategy"])
    url = "https://www.dallasopendata.com/resource/7h2m-3um5.json"

    data = list(read_web_data(url))

    for row in data:
        strategy.output(row)

    write_to_csv(data, "Dallas_Animal_Shelter_Data.csv")
