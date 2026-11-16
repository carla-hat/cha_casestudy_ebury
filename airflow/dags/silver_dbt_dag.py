"""
Silver layer DAG.

Runs the dbt silver models and then their
data quality tests. It is triggered by the bronze Dataset: it starts by itself
when the bronze ingestion DAG finishes successfully.

The silver Dataset is published only by the test task, gold dags start only when the silver tests have passed.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator

from common.dataset import BRONZE_CUSTOMER_TRANSACTIONS, SILVER_CUSTOMER_TRANSACTIONS

# dbt is already installed inside airflow (local solution, not in prd)
DBT = "/home/airflow/dbt_venv/bin/dbt"
DBT_DIR = "/opt/airflow/dbt"
DBT_ARGS = f"--project-dir {DBT_DIR} --profiles-dir {DBT_DIR}"

default_args = {
    "owner": "chatamoto",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="silver_dbt_customer_transactions",
    description="dbt silver layer: clean and type the bronze data, then run its tests",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule=[BRONZE_CUSTOMER_TRANSACTIONS],  # starts when bronze finishes successfully
    catchup=False,
    max_active_runs=1,
    tags=["silver", "staging", "dbt", "transactions", "customers"],
)
def silver_dbt():

    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"{DBT} run --select path:models/silver {DBT_ARGS}",
    )

    dbt_test_silver = BashOperator(
        task_id="dbt_test_silver",
        # models/silver -> the tests declared in schema.yml
        # tests         -> the singular tests (plain SQL files in dbt/tests)
        bash_command=f"{DBT} test --select path:models/silver path:tests/silver {DBT_ARGS}",
        retries=0, 
        outlets=[SILVER_CUSTOMER_TRANSACTIONS],  # published only if the tests pass
    )

    dbt_run_silver >> dbt_test_silver


dag_instance = silver_dbt()
