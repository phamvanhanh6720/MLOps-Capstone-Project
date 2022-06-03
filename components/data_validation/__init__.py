# 1. Log a dataset version as an artifact
import os
import wandb
import pandas as pd
import tensorflow_data_validation as tfdv
from sklearn.model_selection import train_test_split


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

