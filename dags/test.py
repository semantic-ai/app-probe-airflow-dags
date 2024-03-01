from datetime import datetime
import logging

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable


logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}

with DAG(
        dag_id="test",
        schedule_interval="@daily",
        default_args=default_args,
        catchup=False,
        tags=["tests"]
) as dag:
    command = ["python", "-m", "unittest"]

    DockerOperator(
        task_id="test",
        container_name="test",
        image="stadgent/probe-sparql-mono:latest",
        force_pull=True,
        environment={
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "TESTING": "test",
            "GIT_PYTHON_REFRESH": "quiet"
        },
        command=command,
        auto_remove="force"
    )
