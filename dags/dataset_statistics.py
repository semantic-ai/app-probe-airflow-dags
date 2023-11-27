from datetime import datetime
import logging

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.models import Variable
from airflow.models.param import Param

from kubernetes.client import models as k8s

logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}


with DAG(
    dag_id="dataset_statistics",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    params={
        "max_depth": Param(4, type="integer", minimum=1, maximum=10)
    },
    tags=["dataset"]
) as dag:
    KubernetesPodOperator(
        task_id="dataset_statistics",
        name="statistics",
        image="stadgent/probe-sparql-mono:latest",
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always",
        startup_timeout_seconds=480,
        container_resources=k8s.V1ResourceRequirements(limits={"cpu": "2", "memory": "8G"}),
        env_vars={
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "dataset_statistics",
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH": "quiet",
            "TQDM_DISABLE": "1",
            "PYTHONWARNINGS": "ignore"
        },
        cmds=[
            "python",
            "-m",
            "src.dataset_statistics",
            "--max_level={{ params.max_depth }}"
        ]
    )
