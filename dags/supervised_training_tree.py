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
    dag_id="tree_training",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    params={
        "train_flavour": Param("bert", enum=enums.TRAIN_FLAVOURS),
        # "dataset_type": Param("dynamic_general", enum=enums.DATASET_TYPES),
        "taxonomy_uri": Param(
            "http://stad.gent/id/concepts/gent_words", enum=enums.TAXONOMY_URIS
        ),
        "model_id": Param(None, type=["null", "string"]),
        "train_test_split": Param(True, type="boolean"),
        "use_predefined_split": Param(False, type="boolean"),
        "max_depth": Param(2, type="integer", minimum=1, maximum=10),
    },
    tags=["training"],
) as dag:
    command = [
        "python",
        "-m",
        "src.train_supervised_tree",
        "--train_flavour={{ params.train_flavour }}",
        "--dataset_type=dynamic_general",
        "--model_id={{ params.model_id }}",
        "--train_test_split={{ params.train_test_split }}",
        "--max_depth={{ params.max_depth }}",
    ]

    if dag.params.get("taxonomy_uri", None) is not None:
        command += ["--taxonomy_url={{ params.taxonomy_uri }}"]

    KubernetesPodOperator(
        task_id="train_supervised_tree",
        name="train_supervised_tree",
        image="stadgent/probe-sparql-mono:latest",
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always",
        startup_timeout_seconds=480,
        container_resources=k8s.V1ResourceRequirements(
            limits={"cpu": "2", "memory": "16G"}, requests={"cpu": "2", "memory": "8G"}
        ),
        env_vars={
            **EXTRA_ENVS,
            "RUNS_MODEL_PULL_TOKEN": Variable.get("RUNS_MODEL_PULL_TOKEN"),
            "MLFLOW_TRACKING_URI": Variable.get("MLFLOW_TRACKING_URI"),
            "MLFLOW_TRACKING_USERNAME": Variable.get("MLFLOW_TRACKING_USERNAME"),
            "MLFLOW_TRACKING_PASSWORD": Variable.get("MLFLOW_TRACKING_PASSWORD"),
            "MLFLOW_EXPERIMENT_NAME": "train_supervised_tree",
            "REQUEST_AUTH_TYPE": Variable.get("REQUEST_AUTH_TYPE"),
            "REQUEST_USERNAME": Variable.get("REQUEST_USERNAME"),
            "REQUEST_PASSWORD": Variable.get("REQUEST_PASSWORD"),
            "REQUEST_ENDPOINT_DECISION": Variable.get("REQUEST_ENDPOINT_DECISION"),
            "REQUEST_ENDPOINT_TAXONOMY": Variable.get("REQUEST_ENDPOINT_TAXONOMY"),
            "RUNS_DATASET_USE_PREDEFINED_SPLIT": str(
                dag.params.get("use_predefined_split", False)
            ),
            "MLFLOW_TRACKING_INSECURE_TLS": "true",
            "LOGGING_LEVEL": "INFO",
            "GIT_PYTHON_REFRESH": "quiet",
            "TQDM_DISABLE": "1",
        },
        cmds=command,
    )
