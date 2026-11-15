FROM apache/airflow:2.10.5
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m venv /home/airflow/dbt_venv \
    && /home/airflow/dbt_venv/bin/pip install --no-cache-dir \
       "dbt-core==1.9.*" "dbt-postgres==1.9.*"