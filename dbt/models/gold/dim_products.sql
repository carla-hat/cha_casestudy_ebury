select distinct
product_id,
product_name
from analytics_silver.silver_customer_transactions
where product_id is not null and is_valid