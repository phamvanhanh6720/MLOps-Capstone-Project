import pandas as pd
import wandb

import pkg_resources
import importlib
importlib.reload(pkg_resources)

import tensorflow_data_validation as tfdv
from sklearn.model_selection import train_test_split
from tensorflow_data_validation.utils.display_util import get_statistics_html

from components.data_validation import infer_schema, get_schema

import warnings
warnings.filterwarnings("ignore")


run = wandb.init(project="mlops-test", job_type="data-validation")

# Pull down that dataset you logged in the last run
artifact = run.use_artifact('raw-dataset:latest')
artifact_data = artifact.get("raw-dataset")
df = pd.DataFrame(columns=artifact_data.columns, data=artifact_data.data)

# remove unexpected values
df.drop(['_id', 'title', 'url', 'post_date'], axis=1, inplace=True)
df = df.loc[df['external_color'] != '-']
df = df.loc[df['internal_color'] != '-']
df = df.loc[df['fuels'] != '-']
df = df.loc[df['gearbox'] != '-']
df = df.loc[df['wheel_drive'] != '']
df = df.loc[df['wheel_drive'] != '4WD hoặc AWD']

# split data
train_df, test_df = train_test_split(df, train_size=0.9, shuffle=True, random_state=43, stratify=df['branch'])
train_df, val_df = train_test_split(train_df, train_size=0.85, shuffle=True, random_state=43,
                                    stratify=train_df['branch'])

schema = get_schema(run=run, project="mlops-test", is_running=True)
if schema is None:
    schema = infer_schema(
        run=run,
        project='mlops-test',
        artifact_name='raw-dataset:latest',
        filename='raw-dataset',
        is_running=True
    )

# generate statistics
train_stats = tfdv.generate_statistics_from_dataframe(dataframe=train_df)
eva_stats = tfdv.generate_statistics_from_dataframe(dataframe=val_df)
serving_stats = tfdv.generate_statistics_from_dataframe(dataframe=test_df)

# log statistics
file = get_statistics_html(lhs_statistics=eva_stats,
                           rhs_statistics=train_stats,
                           lhs_name='VAL_DATASET',
                           rhs_name='TRAIN_DATASET')
artifact = wandb.Artifact('statistic', type='Statistic')
html = wandb.Html(data=file)
artifact.add(html, 'Statistic')
run.log_artifact(artifact)

# detect anomalies
val_anomalies = tfdv.validate_statistics(
    statistics=eva_stats,
    schema=schema
)
val_anomalies = tfdv.utils.display_util.get_anomalies_dataframe(val_anomalies).reset_index()

serving_anomalies = tfdv.validate_statistics(serving_stats, schema)
serving_anomalies = tfdv.utils.display_util.get_anomalies_dataframe(serving_anomalies).reset_index()

# log anomalies
anomalies_table = wandb.Table(data=val_anomalies, columns=val_anomalies.columns)
run.log({"Val anomalies": anomalies_table})

anomalies_table = wandb.Table(data=serving_anomalies, columns=serving_anomalies.columns)
run.log({"Serving anomalies": anomalies_table})

wandb.finish()
