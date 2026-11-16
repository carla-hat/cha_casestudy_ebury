from airflow.datasets import Dataset

BRONZE_CUSTOMER_TRANSACTIONS = Dataset("postgres://postgres:5432/analytics/bronze/customer_transactions")
SILVER_CUSTOMER_TRANSACTIONS = Dataset("postgres://postgres:5432/analytics/silver/silver_customer_transactions")
GOLD_CUSTOMER_TRANSACTIONS = Dataset("postgres://postgres:5432/analytics/gold/gold_customer_transactions")