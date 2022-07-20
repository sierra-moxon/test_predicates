import requests
from pprint import pprint
import re
from linkml_runtime import SchemaView
from oaklib.implementations.ubergraph.ubergraph_implementation import UbergraphImplementation

oi = UbergraphImplementation()
sv = SchemaView("https://raw.githubusercontent.com/biolink/biolink-model/master/biolink-model.yaml")


def submit_to_endpoint(trapi, api_endpoint):
    response = requests.post(api_endpoint, json=trapi)
    print(response.json()[0])


def fetch_treats_examples():
    r = requests.get('https://smart-api.info/api/metakg')
    metakg = r.json()['associations']
    metakg_small = []
    for association in metakg:
        print("iterate thru metakg")
        # lots of kps don't have an x-trapi, so I can't get the apis from just KPs.
        #if "x-trapi" in association:
        if association.get('api').get('x-translator').get('component') == 'KP':
            if association.get('predicate') in ["treats", "ameliorates", "approved_to_treat"]:
                assoc = {
                    "subject": association.get('subject'),
                    "object": association.get('object'),
                    "predicate": association.get("predicate"),
                    "provided_by": association.get("provided_by"),
                    "api_name": association.get("api").get("name"),
                    "api_id": association.get("api").get("smartapi").get("id"),
                    "id": association.get('subject')+association.get('object')+association.get("predicate")+association.get("api").get("smartapi").get("id")
                }
                metakg_small.append(assoc)

    uniques = list({v['id']: v for v in metakg_small}.values())
    for row in uniques:
        trapi = make_trapi(row.get('subject'), row.get('object'), row.get('predicate'))
        pprint(trapi)
        print("https://smart-api.info/api/metadata/"+row.get('api_id')+"?raw=1")

    return uniques


def query_endpoint():
    rows = fetch_treats_examples()
    for row in rows:
        api_metadata = requests.get("https://smart-api.info/api/metadata/"+row.get('api_id')+"?raw=1")
        trapi = make_trapi(row.get('subject'), row.get('object'), row.get('predicate'))
        pprint(trapi)
        if "x-trapi" in api_metadata.json():
            print("found some x-trapi")
            print(row.get('api_name'))
        #     results = requests.post("https://smart-api.info/ui/"+row.get('api_id')+"/query/query", json=trapi)
        #     pprint(results.json()[0])


def make_trapi(
        subject_category: str,
        object_category: str,
        predicate: str,
        subject_id=None,
        object_id=None
):
    query_graph = {
        "nodes": {
            'a': {
                "category": "biolink:"+subject_category
            },
            'b': {
                "category": "biolink:"+object_category
            }
        },
        "edges": {
            'ab': {
                "subject": "a",
                "object": "b",
                "predicate": "biolink:"+predicate
            }
        }
    }
    if subject_id is not None:
        query_graph['nodes']['a']['id'] = subject_id
    if object_id is not None:
        query_graph['nodes']['b']['id'] = object_id
    message = {"message": {"query_graph": query_graph}, 'knowledge_graph': {"nodes": [], "edges": [], }, 'results': []}
    return message


def uncamelcase(txt: str) -> str:
    split_txt = re.split('(?=[A-Z])', txt)
    new_text = ""
    for word in split_txt:
        if new_text == "":
            new_text = word.lower()
        else:
            new_text = new_text + " " + word.lower()
    return new_text


def get_id_prefixes():
    rows = fetch_treats_examples()
    for row in rows:
        subject = uncamelcase(row.get('subject'))
        element = sv.get_class(subject)
        id_prefixes = []
        if element is None:
            print(subject + " isn't a valid biolink item?")
        elif "id_prefixes" not in element:
            ancestors = sv.class_ancestors(element.name)
            for ancestor in ancestors:
                if sv.get_class(ancestor).id_prefixes is not None:
                    id_prefixes = id_prefixes + sv.get_class(ancestor).id_prefixes
        elif len(element.id_prefixes) != 0 and element.id_prefixes is not None:
            resource = element.id_prefixes[0]
        else:
            print("id prefixes is empty for: " + subject)
