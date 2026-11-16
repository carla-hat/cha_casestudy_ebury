with fact_sum as (
    select count(*) as n, sum(total_amount) as amount
    from analytics_gold.fact_transactions
),
agg_sum as (
    select sum(num_transactions) as n, sum(total_revenue_month) as amount
    from analytics_gold.agg_monthly_sales
)
select fact_sum.n as fact_rows, agg_sum.n as agg_rows, fact_sum.amount as fact_amount, agg_sum.amount as agg_amount
from fact_sum, agg_sum
where fact_sum.n <> agg_sum.n
   or fact_sum.amount <> agg_sum.amount