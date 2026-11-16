select
transaction_id,
customer_id,
product_id,
transaction_date,
quantity,
price as unit_price,
tax,
cast((price * quantity) as numeric(12,2)) + tax as total_amount
from {{ ref('silver_customer_transactions') }}
 where is_valid and transaction_id is not null