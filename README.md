# ELT PIPELINE CASE STUDY EBURY
Pipeline using Airflow, dbt, postgreSQL and the possibility of use in Docker

**Stack:** PostgreSQL 16 · Apache Airflow 2.10 · dbt-core 1.9 (dbt-postgres) · Docker Compose


**Requirements:** Docker and Docker Compose.

```bash
# 1. Create your local environment file and write correct information
cp .env.example .env
#    add user and pwd for postgres and airflow
#    (Linux only) set AIRFLOW_UID to the output of: id -u

# 2. Build and start everything
docker compose up -d --build

# 3. Open Airflow
#    http://localhost:8080   (or port set by AIRFLOW_PORT in .env)
#    user / password: AIRFLOW_ADMIN_USER / AIRFLOW_ADMIN_PASSWORD
#    from your .env 
```

**Run the pipeline**
the pipeline runs automatically on startup


## Architecture
![Pipeline architecture](docs/images/architecture_v2_1.png)
Bronze > Raw copy of the CSV as TEXT. Metadata columns are added. 
Silver > In DBT cleaning of the data, keeping raw columns with the original ones. Flag in order to know if it's a valid column or not
Gold > Only valid rows. One dim and one fact table.

Orchestrated in Airflow using Airflow Datasets. Each layer is independent in running.
2 retries for bronze, 1 silver, 1 gold.

## Repository structure

```
.
├── compose.yaml              # postgres, airflow_db (Airflow metadata), airflow
├── .env.example              # environment variables (copy to .env)
├── data/
│   └── customer_transactions.csv
├── airflow/
│   ├── Dockerfile            # Airflow image + dbt virtualenv
│   ├── requirements.txt
│   └── dags/
│       ├── common/dataset.py # Datasets that chain the DAGs
│       ├── bronze_dag.py
│       ├── silver_dbt_dag.py
│       └── gold_dbt_dag.py
└── dbt/
    ├── dbt_project.yml
    ├── profiles.yml
    ├── models/silver/        # silver model, source and tests
    ├── models/gold/          # dim, fact and aggregate
    └── tests/{silver,gold}/  # singular tests
```

## Data model

- **`dim_products`**: one row per `product_id` (`product_id`, `product_name`).
- **`fact_transactions`**: one row per `transaction_id` (`customer_id`, `product_id`, `transaction_date`, `quantity`, `unit_price`, `tax`, `total_amount`).
  `total_amount = quantity * unit_price + tax`
- **`agg_monthly_sales`**: monthly transactions, units sold and revenue (`total_revenue_month`).

## Data quality

First look at the raw CSV showed different problems:
- Prefix in transaction_id
- Different date formats
- Numbers written with words
- Decimals in integer fields
- Missing values in different columns

