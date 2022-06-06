import os
import wandb
import pandas as pd

import pkg_resources
import importlib

import tensorflow_data_validation as tfdv
from sklearn.model_selection import train_test_split
from tensorflow_data_validation.utils.display_util import get_statistics_html

import warnings
warnings.filterwarnings("ignore")
importlib.reload(pkg_resources)


def infer_schema(project: str, artifact_name='raw-dataset:latest', filename='raw-dataset', is_running=True, run=None):
    # Initialize a new W&B run to track this job
    if not is_running:
        run = wandb.init(project=project, job_type="infer-schema")

    # Create a sample dataset to log as an artifact
    artifact = run.use_artifact(artifact_name)
    artifact_data = artifact.get(filename)
    df = pd.DataFrame(columns=artifact_data.columns, data=artifact_data.data)

    df = df.loc[df['external_color'] != '-']
    df = df.loc[df['internal_color'] != '-']
    df = df.loc[df['fuels'] != '-']
    df = df.loc[df['gearbox'] != '-']
    df = df.loc[df['wheel_drive'] != '']
    df = df.loc[df['wheel_drive'] != '4WD hoặc AWD']

    df.drop(['_id', 'title', 'url', 'post_date'], axis=1, inplace=True)
    train_df, test_df = train_test_split(df, train_size=0.9, shuffle=True, random_state=43, stratify=df['branch'])
    train_stats = tfdv.generate_statistics_from_dataframe(dataframe=train_df)
    schema = tfdv.infer_schema(statistics=train_stats)
    schema_df_result = tfdv.utils.display_util.get_schema_dataframe(schema=schema)

    # log schema
    artifact = wandb.Artifact('categorical-schema', type='Schema')
    categorical_schema = schema_df_result[1].reset_index()
    schema_table = wandb.Table(data=categorical_schema, columns=categorical_schema.columns)
    artifact.add(schema_table, 'categorical-schema-table')
    run.log_artifact(artifact)

    artifact = wandb.Artifact('data-schema', type='Schema')
    data_schema = schema_df_result[0].reset_index()
    schema_table = wandb.Table(data=data_schema, columns=data_schema.columns)
    artifact.add(schema_table, 'data-schema-table')
    run.log_artifact(artifact)

    tfdv.write_schema_text(schema=schema, output_path='schema.txt')
    artifact = wandb.Artifact('text-schema', type='Schema')
    artifact.add_file('schema.txt')
    run.log_artifact(artifact)

    if not is_running:
        wandb.finish()


def get_schema(project, artifact_name='text-schema:latest', is_running=True, run=None):
    if not is_running:
        run = wandb.init(project=project, job_type="download-schema")
    schema = None

    try:
        artifact = run.use_artifact(artifact_name)
        artifact_dir = artifact.download()
        schema = tfdv.load_schema_text(os.path.join(artifact_dir, 'schema.txt'))
        if not is_running:
            wandb.finish()
    except:
        if not is_running:
            wandb.finish(exit_code=1)
        pass

    return schema


def validate_data(project):
    run = wandb.init(project=project, job_type="data-validation")
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

    # log train, val, test data
    dataset_artifact = wandb.Artifact('train-data', type='dataset')
    dataset_table = wandb.Table(data=train_df, columns=train_df.columns)
    dataset_artifact.add(dataset_table, 'train-data')
    run.log_artifact(dataset_artifact)

    dataset_artifact = wandb.Artifact('val-data', type='dataset')
    dataset_table = wandb.Table(data=val_df, columns=val_df.columns)
    dataset_artifact.add(dataset_table, 'val-data')
    run.log_artifact(dataset_artifact)

    dataset_artifact = wandb.Artifact('test-data', type='dataset')
    dataset_table = wandb.Table(data=val_df, columns=val_df.columns)
    dataset_artifact.add(dataset_table, 'test-data')
    run.log_artifact(dataset_artifact)

    schema = get_schema(run=run, project=project, is_running=True)
    if schema is None:
        schema = infer_schema(
            run=run,
            project=project,
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

