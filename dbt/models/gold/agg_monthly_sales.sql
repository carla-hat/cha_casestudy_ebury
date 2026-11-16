-- Monthly totals. Useful for trend / revenue reporting.
select
    cast(date_trunc('month', transaction_date) as date) as month,
    count(*) as num_transactions,
    sum(quantity)               as units_sold,
    sum(total_amount) as total_revenue_month
from analytics_gold.fact_transactions
group by 1
