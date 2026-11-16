-- Fails if a transaction date is in the future or tooo old.
select *
from silver.silver_customer_transactions
where transaction_date > current_date
   or transaction_date < date '1900-01-01'
