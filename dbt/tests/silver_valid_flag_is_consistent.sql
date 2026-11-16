-- Fails if is_valid disagrees with pending_values:
-- a row must be valid only when it has no pending issue.
select *
from silver.silver_customer_transactions
where is_valid <> (cardinality(pending_values) = 0)
