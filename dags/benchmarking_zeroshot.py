from datetime import datetime
import logging

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.models import Variable

from kubernetes.client import models as k8s

logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}


with DAG(
    dag_id="zeroshot_benchmarking",
    schedule_interval="@once",
    default_args=default_args,
    catchup=False,
    params={
        "model_types": ["zeroshot"],
        "dataset_types": ["m1"],
        "taxonomy_uri": "http://stad.gent/id/concepts/gent_words",
        "model_ids": [
            "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
            "facebook/bart-large-mnli",
            "mjwong/multilingual-e5-base-xnli-anli",
            "joeddav/xlm-roberta-large-xnli"
        ]
    },
    tags=["benchmarking"]
) as dag:
    KubernetesPodOperator(
        task_id="zeroshot_benchmarking",
        name="zeroshot",
        image="stadgent/probe-sparql-mono:latest",
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always",
        startup_timeout_seconds=480,
        env_vars={
            "HF_ACCESS_TOKEN": Variable.get("HF_ACCESS_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "zeroshot_benchmarking",
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH":"quiet",
            "TQDM_DISABLE": "1",
            "PYTHONWARNINGS": "ignore"
        },
        cmds=[
            "python",
            "-m",
            "src.benchmarking",
            "--model_types={{ params.model_types }}",
            "--dataset_types={{ params.dataset_types }}",
            "--model_ids={{ params.model_ids }}",
            "--taxonomy_uri={{ params.taxonomy_uri }}"
        ]
    )
