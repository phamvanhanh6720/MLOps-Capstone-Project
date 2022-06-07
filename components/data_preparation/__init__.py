import pandas as pd
import wandb

import category_encoders as ce
from scipy import stats
import numpy as np
import utils


CONFIG_DATA ={
    "numeric":{
        "year":{
            "lower_limit": 2007,
            "upper_limit":float('inf')
        },
        "km_driven":{
            "lower_limit": 0,
            "upper_limit":1e9
        },
        "num_seats": {
            "lower_limit": 0,
            "upper_limit":30
        },
        "engine_capacity":{
            "lower_limit": 0,
            "upper_limit": 10
        }
    },
    "category": {
        "origin": ['domestic', 'imported'],
        "wheel_drive": ['FWD', 'RWD', '4WD', 'AWD'],
        "car_type": ['sedan', 'crossover', 'hatchback', 'pickup', 'suv', 'van', 'coupe',
                    'truck', 'convertible', 'wagon'],
        "gearbox": ['automatic', 'manual']
    }
}

category_other = ['external_color','internal_color','origin', 'gearbox', 'wheel_drive', 'car_type']

numeric_features = ['year','price','km_driven','num_seats','engine_capacity']
category_features = ['branch','model','origin','external_color','internal_color','gearbox','wheel_drive','car_type']
FEATURES = numeric_features + category_features


def detect_outline(df: pd.DataFrame, feature: str, lower_limit: float = 0,
                   upper_limit: float = float('inf')) -> pd.DataFrame:
    """
    Remove outline of features
    """
    return df[(df[feature] < upper_limit) & (df[feature] > lower_limit)]


def filter_numeric_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outline for feature numeric
    """
    df = detect_outline(df=df, feature='year', lower_limit=CONFIG_DATA['numeric']['year']['lower_limit'])
    df = detect_outline(df=df, feature='km_driven', upper_limit=CONFIG_DATA['numeric']['km_driven']['upper_limit'])
    df = detect_outline(df=df, feature='num_seats', upper_limit=CONFIG_DATA['numeric']['num_seats']['upper_limit'])
    df = detect_outline(df=df, feature='engine_capacity',
                        upper_limit=CONFIG_DATA['numeric']['engine_capacity']['upper_limit'])
    return df


def filter_category_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outline for feature category
    """
    df = df.loc[df.origin.apply(lambda x: x in CONFIG_DATA['category']['origin'])]
    df = df.loc[df.wheel_drive.apply(lambda x: x in CONFIG_DATA['category']['wheel_drive'])]
    df = df.loc[df.car_type.apply(lambda x: x in CONFIG_DATA['category']['car_type'])]
    df = df.loc[df.gearbox.apply(lambda x: x in CONFIG_DATA['category']['gearbox'])]
    return df


def filter_outline_target(df: pd.DataFrame, z_score: float = 2.8) -> pd.DataFrame:
    df = df[(np.abs(stats.zscore(df.price)) < z_score)]
    return df


class Transform:
    def __init__(self, df_train, df_test, df_val) -> None:
        self.df_train = df_train
        self.df_test = df_test
        self.df_val = df_val

        # init encoder
        self.encoder_branch = ce.JamesSteinEncoder()
        self.encoder_model = ce.JamesSteinEncoder()
        self.encoder_others = ce.OrdinalEncoder()

    def fit(self) -> None:
        self.encoder_branch.fit(self.df_train['branch'], self.df_train['price'])
        self.encoder_model.fit(self.df_train['model'], self.df_train['price'])
        self.encoder_others.fit(self.df_train[category_other])

    def transform(self) -> None:
        self.df_train['branch'] = self.encoder_branch.transform(self.df_train['branch'])
        self.df_train['model'] = self.encoder_model.transform(self.df_train['model'])
        self.df_train[category_other] = self.encoder_others.transform(self.df_train[category_other])

        self.df_test['branch'] = self.encoder_branch.transform(self.df_test['branch'])
        self.df_test['model'] = self.encoder_model.transform(self.df_test['model'])
        self.df_test[category_other] = self.encoder_others.transform(self.df_test[category_other])

        self.df_val['branch'] = self.encoder_branch.transform(self.df_val['branch'])
        self.df_val['model'] = self.encoder_model.transform(self.df_val['model'])
        self.df_val[category_other] = self.encoder_others.transform(self.df_val[category_other])

    def save(self) -> None:
        utils.save_pkl(self.encoder_branch, 'branch-func.pkl')
        utils.save_pkl(self.encoder_model, 'model-func.pkl')
        utils.save_pkl(self.encoder_others, 'other-func.pkl')


def prepare_data(project):
    # Load data
    run = wandb.init(project=project, job_type="data-preparation")
    artifact = run.use_artifact('train-data:latest')
    artifact_data = artifact.get("train-data")
    df_train = pd.DataFrame(columns=artifact_data.columns, data=artifact_data.data)

    artifact = run.use_artifact('val-data:latest')
    artifact_data = artifact.get("val-data")
    df_val = pd.DataFrame(columns=artifact_data.columns, data=artifact_data.data)

    artifact = run.use_artifact('test-data:latest')
    artifact_data = artifact.get("test-data")
    df_test = pd.DataFrame(columns=artifact_data.columns, data=artifact_data.data)

    # Process missing data
    mode = df_train.wheel_drive.mode()[0]
    mean = float(int(df_train.engine_capacity.mean()))
    df_train['wheel_drive'].fillna(value=mode, inplace=True)
    df_val['wheel_drive'].fillna(value=mode, inplace=True)
    df_test['wheel_drive'].fillna(value=mode, inplace=True)
    df_train['engine_capacity'].fillna(value=mean, inplace=True)
    df_val['engine_capacity'].fillna(value=mean, inplace=True)
    df_test['engine_capacity'].fillna(value=mean, inplace=True)

    # Filter outline
    df_train = filter_outline_target(df_train)
    df_test = filter_outline_target(df_test)
    df_val = filter_outline_target(df_val)

    df_train = filter_category_feature(filter_numeric_feature(df_train))
    df_test = filter_category_feature(filter_numeric_feature(df_test))
    df_val = filter_category_feature(filter_numeric_feature(df_val))

    # Transform data
    transform = Transform(df_train, df_test, df_val)
    transform.fit()
    transform.transform()
    transform.save()
    # log transform func
    artifact = wandb.Artifact('branch-func', type='Transform')
    artifact.add_file('branch-func.pkl')
    run.log_artifact(artifact)

    artifact = wandb.Artifact('model-func', type='Transform')
    artifact.add_file('model-func.pkl')
    run.log_artifact(artifact)

    artifact = wandb.Artifact('other-func', type='Transform')
    artifact.add_file('other-func.pkl')
    run.log_artifact(artifact)

    transformed_train_df = transform.df_train[FEATURES]
    transformed_val_df = transform.df_val[FEATURES]
    transformed_test_df = transform.df_test[FEATURES]

    dataset_artifact = wandb.Artifact('transformed-train-data', type='dataset')
    dataset_table = wandb.Table(data=transformed_train_df, columns=transformed_train_df.columns)
    dataset_artifact.add(dataset_table, 'transformed-train-data')
    run.log_artifact(dataset_artifact)

    dataset_artifact = wandb.Artifact('transformed-val-data', type='dataset')
    dataset_table = wandb.Table(data=transformed_val_df, columns=transformed_val_df.columns)
    dataset_artifact.add(dataset_table, 'transformed-val-data')
    run.log_artifact(dataset_artifact)

    dataset_artifact = wandb.Artifact('transformed-test-data', type='dataset')
    dataset_table = wandb.Table(data=transformed_test_df, columns=transformed_test_df.columns)
    dataset_artifact.add(dataset_table, 'transformed-test-data')
    run.log_artifact(dataset_artifact)

    wandb.finish()
