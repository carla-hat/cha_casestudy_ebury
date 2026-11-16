-- Fails if silver has a different number of rows than bronze.
with bronze_count as (
    select count(*) as total_bronze
    from bronze.customer_transactions
),
silver_count as (
    select count(*) as total_silver
    from analytics_silver.silver_customer_transactions
)
select
    bronze_count.total_bronze as bronze_rows,
    silver_count.total_silver as silver_rows
from bronze_count, silver_count
where bronze_count.total_bronze <> silver_count.total_silver
