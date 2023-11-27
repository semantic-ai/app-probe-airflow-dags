from datetime import datetime
import logging
import enums

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.models.param import Param
from airflow.models import Variable

from kubernetes.client import models as k8s

logging.basicConfig(level=logging.INFO)

default_args = {
    "start_date": datetime(2023, 1, 1),
    "owner": "Airflow",
}

with DAG(
        dag_id="inference_w_config",
        schedule_interval=None,
        default_args=default_args,
        catchup=False,
        params={
            "dataset_type": Param("m1_general", enum=enums.DATASET_TYPES),
            "model_config": Param(enums.INFERENCE_CONFIG_EXAMPLE, type=["object", "null"]),
            "taxonomy_uri": Param("http://stad.gent/id/concepts/business_capabilities", enum=enums.TAXONOMY_URIS),
        },
        tags=["inference"]
) as dag:
    command = [
        "python",
        "-m",
        "src.inference_with_config",
        "--dataset_type={{ params.dataset_type }}",
        "--model_config='{{ params.model_config }}'",
        "--taxonomy_uri={{ params.taxonomy_uri }}"

    ]

    KubernetesPodOperator(
        task_id="inference_with_config",
        name="inference_with_config",
        image="stadgent/probe-sparql-mono:latest",
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always",
        startup_timeout_seconds=480,
        container_resources=k8s.V1ResourceRequirements(limits={"cpu": "4", "memory": "16G"}),
        env_vars={
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "inference_with_config",
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH": "quiet",
            "TQDM_DISABLE": "1"
        },
        cmds=command

    )
