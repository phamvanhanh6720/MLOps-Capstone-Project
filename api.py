import os
import pickle
from typing import Optional
from pydantic import BaseModel

import wandb
import pandas as pd
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


class Input(BaseModel):
    year: int
    location: str
    branch: str
    model: str
    origin: str
    km_driven: int
    external_color: str
    internal_color: str
    num_seats: int
    fuels: str
    engine_capacity: float
    gearbox: str
    wheel_drive: str
    car_type: str


api = FastAPI(title="MLOps", version='0.1.0')
origins = ["*"]
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

run = wandb.init(project='mlops', job_type='serving')
artifact = run.use_artifact('phamvanhanh6720/mlops/model:product', type='Model')
artifact_dir = artifact.download()
run.finish()

with open(os.path.join(artifact_dir, 'model.pkl'), 'rb') as file:
    model = pickle.load(file)

with open(os.path.join('stores', 'branch.pkl'), 'rb') as file:
    transform_branch = pickle.load(file)

with open(os.path.join('stores', 'model.pkl'), 'rb') as file:
    transform_model = pickle.load(file)

with open(os.path.join('stores', 'others.pkl'), 'rb') as file:
    transform_other = pickle.load(file)

category_other = ['external_color', 'internal_color', 'origin', 'gearbox', 'wheel_drive', 'car_type']
numeric_features = ['year','km_driven','num_seats','engine_capacity']
category_features = ['branch','model','origin','external_color','internal_color','gearbox','wheel_drive','car_type']
FEATURES = numeric_features + category_features


@api.post('/api/predict')
def predict(input: Input):
    value = [input.year, input.location, input.branch, input.model,
             input.origin, input.km_driven, input.external_color, input.internal_color,
             input.num_seats, input.fuels, input.engine_capacity, input.gearbox,
             input.wheel_drive, input.car_type]

    column = ['year', 'location', 'branch', 'model', 'origin', 'km_driven',
              'external_color', 'internal_color', 'num_seats', 'fuels', 'engine_capacity',
              'gearbox', 'wheel_drive', 'car_type']

    df = pd.DataFrame(data=[value], columns=column)

    df['branch'] = transform_branch.transform(df['branch'])
    df['model'] = transform_model.transform(df['model'])
    df[category_other] = transform_other.transform(df[category_other])
    df = df[FEATURES]

    price = model.predict(df)[0]

    return {'price': price}

