import logging
from datetime import datetime

import enums
from airflow import DAG
from airflow.models import Variable
from airflow.models.param import Param
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from enums import EXTRA_ENVS
from kubernetes.client import models as k8s

logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}


with DAG(
    dag_id="benchmark_zeroshot",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    params={
        "model_types": Param(
            ["zeroshot"],
            type="array",
            examples=[t for t in enums.MODEL_TYPES if t.startswith("zeroshot")]
            + ["zeroshot"],
        ),
        "dataset_types": Param(
            ["m1"], type="array", examples=enums.DATASET_TYPES + ["m1", "m2"]
        ),
        "taxonomy_uri": Param(
            "http://stad.gent/id/concepts/gent_words", enum=enums.TAXONOMY_URIS
        ),
        "model_ids": enums.ZEROSHOT_MODELS,
    },
    tags=["benchmarking"],
) as dag:
    KubernetesPodOperator(
        task_id="benchmark_zeroshot",
        name="zeroshot",
        image="stadgent/probe-sparql-mono:latest",
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always",
        startup_timeout_seconds=480,
        container_resources=k8s.V1ResourceRequirements(
            limits={"cpu": "2", "memory": "12G"}, requests={"cpu": "2", "memory": "4G"}
        ),
        env_vars={
            **EXTRA_ENVS,
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "zeroshot_benchmarking",
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "MLFLOW_TRACKING_INSECURE_TLS": "true",
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH": "quiet",
            "TQDM_DISABLE": "1",
            "PYTHONWARNINGS": "ignore",
        },
        cmds=[
            "python",
            "-m",
            "src.benchmarking",
            "--model_types={{ params.model_types }}",
            "--dataset_types={{ params.dataset_types }}",
            "--model_ids={{ params.model_ids }}",
            "--taxonomy_uri={{ params.taxonomy_uri }}",
        ],
    )
