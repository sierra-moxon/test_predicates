from src.treats import treats
import requests
from pprint import pprint


def test_treats():
    # response = requests.get("https://smart-api.info/api/metadata/978fe380a147a8641caf72320862697b?raw=1", timeout=5)
    # pprint(response.json())
    treats.fetch_treats_examples()


def test_get_id_prefixes():
    treats.get_id_prefixes()


def test_query_endpoint():
    treats.query_endpoint()
