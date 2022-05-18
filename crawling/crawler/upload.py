import json
import requests
import datetime


def default_converter(object):
    if isinstance(object, datetime.date):
        return object.__str__()


def upload_document(
        app_id: str,
        api_key: str,
        database: str,
        collection: str,
        data_source: str,
        document: dict
):
    url = "https://data.mongodb-api.com/app/{}/endpoint/data/beta/action/insertOne".format(app_id)

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': api_key
    }

    body = json.dumps({
        "collection": collection,
        "database": database,
        "dataSource": data_source,
        "document": document},
        default=default_converter
    )

    try:
        requests.request("POST", url, headers=headers, data=body)
    except:
        raise Exception("Upload document fail")


def replace_document(
        app_id: str,
        api_key: str,
        database: str,
        collection: str,
        data_source: str,
        filter: dict,
        replacement: dict
):
    url = "https://data.mongodb-api.com/app/{}/endpoint/data/beta/action/replaceOne".format(app_id)
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': api_key
    }

    body = json.dumps({
        "collection": collection,
        "database": database,
        "dataSource": data_source,
        "filter": filter,
        "replacement": replacement,
        "upsert": True},
        default=default_converter
    )

    requests.request("POST", url, headers=headers, data=body)

