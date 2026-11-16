-- a row must be valid only when it has no pending issue.
select *
from  analytics_silver.silver_customer_transactions
where is_valid <> (cardinality(pending_values) = 0)
