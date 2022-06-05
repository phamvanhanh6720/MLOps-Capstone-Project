import json
import pandas as pd
from configs.config import *
import utils

def load_transform():
    transform_branch = utils.load_pkl(PATH_TRANSFORM_BRANCH)
    transform_model = utils.load_pkl(PATH_TRANSFORM_MODEL)
    transform_other = utils.load_pkl(PATH_TRANSFORM_OTHERS)
    return transform_branch, transform_model, transform_other


def load_mode():
    return utils.load_pkl(PATH_BEST_MODEL)


def run(input: list):
    model = load_mode()
    transform_branch, transform_model, transform_other = load_transform()
    df = pd.DataFrame(input)
    df['branch'] = transform_branch.transform(df['branch'])
    df['model'] = transform_model.transform(df['model'])
    df[category_other] = transform_other.transform(df[category_other])
    return model.predict(df)