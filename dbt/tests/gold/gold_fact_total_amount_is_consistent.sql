select *
from analytics_gold.fact_transactions
where abs(total_amount - (quantity * unit_price + tax)) > 0.01