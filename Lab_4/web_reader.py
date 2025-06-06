import requests


def read_web_data(url: str):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    for item in data:
        yield item
