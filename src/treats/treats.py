import json
import pandas as pd
import requests
import csv
from pprint import pprint
import sqlite3
from linkml_runtime import SchemaView
from linkml_runtime.utils import formatutils
from oaklib.implementations.ubergraph.ubergraph_implementation import UbergraphImplementation
from sqlalchemy import create_engine


oi = UbergraphImplementation()
conn = sqlite3.connect('test.db')
sv = SchemaView("https://raw.githubusercontent.com/biolink/biolink-model/master/biolink-model.yaml")


def run():
    engine = create_engine('sqlite://',
                           echo=False)

    r = requests.get('https://smart-api.info/api/metakg')
    metakg = r.json()['associations']
    metakg_small = []
    for association in metakg:
        if association.get('api').get('x-translator').get('component') == 'KP':
            assoc = {
                "subject": association.get('subject'),
                "object": association.get('object'),
                "predicate": association.get("predicate"),
                "provided_by": association.get("provided_by"),
                "api_name": association.get("api").get("name"),
                "api_id": association.get("api").get("smartapi").get("id")
            }
            metakg_small.append(assoc)

    metakg_df = pd.DataFrame.from_dict(metakg_small)
    engine.execute("drop table if exists metakg_table")
    metakg_df.to_sql('metakg_table',
                     con=engine)

    df = pd.read_sql(
        'SELECT distinct subject, object, provided_by, predicate, api_name, '
        'api_id from metakg_table where predicate = "ameliorates" or '
        'predicate = "approved_to_treat" or predicate = "treats"',
        engine)
    # write DataFrame to CSV file
    # df.to_csv('metakg.csv', index=False)
    rows = df.to_dict('records')
    return rows


def query_endpoint():
    rows = run()
    for row in rows:
        trapi = make_trapi(row.get('subject'), row.get('object'), row.get('predicate'))
        print(trapi)
    return None


def make_trapi(subject: str, object: str, predicate: str):
    return ""


def get_id_prefixes():
    rows = run()
    for row in rows:
        subject = "biolink:"+formatutils.camelcase(row.get('subject'))
        element = sv.get_class(row.get('subject'))
        id_prefixes = []
        if element is None:
            print(row.get('subject'))
            print(subject + " isn't a valid biolink item?")
        elif "id_prefixes" not in element:
            ancestors = sv.class_ancestors(element.name)
            for ancestor in ancestors:
                if sv.get_class(ancestor).id_prefixes is not None:
                    id_prefixes = id_prefixes + sv.get_class(ancestor).id_prefixes
        elif len(element.id_prefixes) != 0:
            resource = id_prefixes[0]
            print(resource)
        else:
            print("id prefixes is empty for: " + subject)