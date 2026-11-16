select *
from analytics_gold.fact_transactions
where quantity   <= 0
   or tax        <  0