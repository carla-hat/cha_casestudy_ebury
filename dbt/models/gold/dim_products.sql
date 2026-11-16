select distinct
product_id,
product_name
from {{ ref('silver_customer_transactions') }}
where product_id is not null and is_valid