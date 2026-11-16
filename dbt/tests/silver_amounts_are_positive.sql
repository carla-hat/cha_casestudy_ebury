-- Fails if any row has a non-positive price or quantity, or a negative tax.
select *
from silver.silver_customer_transactions
where quantity <= 0
   or tax      <  0
