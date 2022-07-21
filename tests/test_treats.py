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
    treats.get_unique_metadata_endpoints()


def test_run_it():
    #"https://smart-api.info/ui/03c1982f2e3ba3710da20aa9c01a00f6/reasoner_api_query_post/"
    # https://automat.renci.org/drugcentral/1.2/query
    trapi = {'message': {'query_graph': {'nodes': {'a': {'category': 'biolink:SmallMolecule'}, 'b': {'category': 'biolink:Disease'}}, 'edges': {'ab': {'subject': 'a', 'object': 'b', 'predicate': 'biolink:treats'}}}}}
    #
    response = requests.post("https://automat.renci.org/robokopkg/1.2/query", json=trapi)
    print(response.status_code)
    # pprint(response.json())
    treats.run_it()
