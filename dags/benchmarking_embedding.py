from datetime import datetime
import enums
import logging

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from airflow.models.param import Param

from enums import EXTRA_ENVS


logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}

with DAG(
    dag_id="benchmark_embedding",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    params={
        "model_types": Param(["embedding"], type="array", examples=[t for t in enums.MODEL_TYPES if t.startswith("embedding")] + ["embedding"]),
        "dataset_types": Param(["m1"], type="array", examples=enums.DATASET_TYPES + ["m1", "m2"]),
        "taxonomy_uri": Param("http://stad.gent/id/concepts/gent_words", enum=enums.TAXONOMY_URIS),
        "model_ids": enums.EMBEDDING_MODELS
    },
    tags=["benchmarking"]
) as dag:
    command = [
        "python",
        "-m",
        "src.benchmarking",
        "--model_types={{ params.model_types }}",
        "--dataset_types={{ params.dataset_types }}",
        "--model_ids={{ params.model_ids }}"
    ]

    DockerOperator(
        task_id="benchmark_embedding",
        container_name="embedding",
        image="stadgent/probe-sparql-mono:latest",
        force_pull=True,
        network_mode="probe",
        environment={
            **EXTRA_ENVS,
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "embedding_benchmarking",
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "MLFLOW_TRACKING_INSECURE_TLS": "true",
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH": "quiet",
            "TQDM_DISABLE": "1",
            "PYTHONWARNINGS": "ignore"
        },
        command=command,
        auto_remove="force"
    )
