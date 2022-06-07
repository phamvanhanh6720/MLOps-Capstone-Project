import json
import requests
import pandas as pd

import wandb
from decouple import config


def fetch_data():
    url = "https://data.mongodb-api.com/app/data-zbxno/endpoint/data/beta/action/find"

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': config('MONGO_API_KEY')
    }

    body = json.dumps({
        "dataSource": "Cluster-MLOps-Database",
        "database": "datawarehouse",
        "collection": "data",
        "filter": {},
        "limit": 50000

    })

    request = requests.request("POST", url, headers=headers, data=body)
    if request.status_code != 200:
        raise Exception('Fetch data failed')

    json_list = json.loads(request.text)['documents']
    df = pd.DataFrame.from_records(json_list)

    return df


def extract_data(project):
    run = wandb.init(project=project, job_type="data-extraction")

    # Create a sample dataset to log as an artifact
    df = fetch_data()

    # log data artifacts
    dataset_artifact = wandb.Artifact('raw-dataset', type='dataset')
    dataset_table = wandb.Table(data=df, columns=df.columns)
    dataset_artifact.add(dataset_table, 'raw-dataset')
    run.log_artifact(dataset_artifact)

    wandb.finish()