from datetime import datetime
import enums
import logging

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from airflow.models.param import Param


logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}

with DAG(
    dag_id="dataset_export",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    params={
        "dataset_type": Param("mirror", enum=enums.DATASET_TYPES),
        "taxonomy_uri": Param("http://stad.gent/id/concepts/gent_words", enum=enums.TAXONOMY_URIS)
    },
    tags=["dataset"]
) as dag:
    command = [
        "python",
        "-m",
        "src.dataset_export",
        "--dataset_type={{params.dataset_type}}",
        "--taxonomy_uri={{params.taxonomy_uri}}"
    ]

    DockerOperator(
        task_id="dataset_export",
        container_name="export",
        image="stadgent/probe-sparql-mono:latest",
        force_pull=True,
        environment={
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "dataset_export",
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "MLFLOW_TRACKING_INSECURE_TLS": "true",
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH": "quiet",
            "TQDM_DISABLE": "1",
            "PYTHONWARNINGS": "ignore"
        },
        command=command,
        auto_remove="force"
    )
