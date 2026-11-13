"""
Bronze layer ingestion DAG.

Loads the raw customer_transactions CSV into PostgreSQL (schema `bronze`)
without transforming it: every source column is stored as TEXT and
metzadata columns are added (_ting, _lsrcfil, _lotid).
Cleaning / typing is done later in the silver layer (dbt).
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta, timezone

import pandas as pd
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import create_engine, inspect, text
from airflow.exceptions import AirflowException


log = logging.getLogger(__name__)

CSV_FILE_PATH = "/opt/airflow/data"
POSTGRES_CONN_ID = "postgres_analytics"
BRONZE_SCHEMA = "bronze"
META_COLUMNS = ["_ting", "_lsrcfil", "_lotid"]

default_args = {
    "owner": "chatamoto",
    "depends_on_past": False,
    "email_on_failure": True,
    "email":["hitacarla3c@gmail.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

def table_name_from(file_name: str) -> str:
    """customer_transactions.csv -> customer_transactions"""
    root = os.path.splitext(file_name)[0].lower().replace("-", "_")
    return root


def get_engine():
    ##connection
    pg_hook = PostgresHook(postgres_conn_id='postgres_analytics')
    db_url = pg_hook.get_uri()
    gest_engine = create_engine(db_url)
    return gest_engine

@dag(
    dag_id="bronze_ingestion_csv",
    description="Raw ingestion of customer transactions into table postgreSQL",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule=None,  # manual if not cron or for ex "@daily" if every day
    catchup=False, #from the past if we want change true
    max_active_runs=1,
    tags=["bronze", "ingestion", "postgres", "transactions", "customers"],
)

def ppl_ingestion():

    @task
    def list_of_files() -> list[str]:
        
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"Path {CSV_FILE_PATH} doesn't match. please check the volume in compose.yaml.")
        #check csv files
        csv_files = [f for f in os.listdir(CSV_FILE_PATH) if f.endswith('.csv')]
        if not csv_files:
            raise AirflowException("CSV files don't found in data/.")
        
        logging.info(f" CSV files detected: {csv_files}")
        return csv_files

    @task
    def create_table(csv_files: list[str]) -> None:

        engine = get_engine()
        with engine.begin() as connexion:
            for file in csv_files:

                table = table_name_from(file)

                columns = pd.read_csv(CSV_FILE_PATH+'/'+file, nrows=0, dtype=str).columns
                columns_desc = ", ".join(f'"{c}" TEXT' for c in columns)
                connexion.execute(text(
                    f"""
                    CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.{table} (
                        {columns_desc},
                        _ting TIMESTAMP NOT NULL DEFAULT NOW(),
                        _lsrcfil TEXT,
                        _lotid TEXT
                    )
                    """
                ))
                logging.info(f"--------------Table {table} is ready")

    @task            
    def load_table(csv_files: list[str], lotid: str) -> int:

        engine= get_engine()
        for file in csv_files:
                        
                table = table_name_from(file)
                logging.info(f"--------------Charging {file} into table  {table}")

                df = pd.read_csv(CSV_FILE_PATH+'/'+file, dtype=str, keep_default_na=False)

                # adding metadata
                df["_ting"] = datetime.now(timezone.utc)
                df["_lsrcfil"] = file
                df["_lotid"] = lotid

                with engine.begin() as connexion:
                   connexion.execute(text(f"TRUNCATE TABLE {BRONZE_SCHEMA}.{table}"))
                   df.to_sql(
                        name=table,
                        con=connexion,
                        schema=BRONZE_SCHEMA,
                        if_exists="append",
                        index=False,
                        method="multi",
                        chunksize=1000,
                    )
                logging.info(f"Table {table} has been loaded with data") 
                row_table = len(df)
                logging.info(f"{row_table} rows have been charged") 
        return row_number

    @task
    def validate_load(row_number: int) -> None:
        return None



    files = list_of_files()
    tables = create_table(files)
    num_row = load_table(files, "{{ run_id }}")
    validate_load(num_row)

dag_instance = ppl_ingestion()
