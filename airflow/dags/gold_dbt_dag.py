"""
Gold layer DAG.

It builds dimension, fact and an aggregate table.
Runs the dbt gold models and then their
data quality tests. It is triggered by the silver Dataset: it starts by itself
when the silver transformations finish successfully.

The silver Dataset is published only by the test task, gold dags start only when the silver tests have passed.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.bash import BashOperator

from common.dataset import GOLD_CUSTOMER_TRANSACTIONS, SILVER_CUSTOMER_TRANSACTIONS

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
    dag_id="gold_dbt_customer_transactions",
    description="dbt gold layer: builds dim and fact and agg, then run its tests",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule=[SILVER_CUSTOMER_TRANSACTIONS],  # starts when SILVER finishes successfully
    catchup=False,
    max_active_runs=1,
    tags=["gold", "modeling", "dbt", "transactions", "customers"],
)
def gold_dbt():

    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"{DBT} run --select path:models/gold {DBT_ARGS}",
    )

    dbt_test_gold = BashOperator(
        task_id="dbt_test_gold",
        # models/gold -> the tests declared in schema.yml
        bash_command=f"{DBT} test --select path:models/gold path:tests/gold {DBT_ARGS}",
        retries=0, 
        outlets=[GOLD_CUSTOMER_TRANSACTIONS],  # published only if the tests pass
    )

    dbt_run_gold >> dbt_test_gold


dag_instance = gold_dbt()
