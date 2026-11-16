with source as (
    select * from {{ source('bronze', 'customer_transactions') }}
),

cleaned as (
    select

        cast(nullif(regexp_replace(transaction_id, '[^0-9]', '', 'g'), '') as integer) as transaction_id,
    
        cast(cast(case when trim(customer_id) ~ '^[0-9]+(\.[0-9]+)?$' then trim(customer_id) end as numeric)as integer)as customer_id,

        case
            when trim(transaction_date) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' then to_date(trim(transaction_date), 'YYYY-MM-DD')
            when trim(transaction_date) ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' then to_date(trim(transaction_date), 'DD-MM-YYYY')
        end as transaction_date,

        cast(nullif(regexp_replace(product_id, '[^0-9]', '', 'g'), '')as integer) as product_id,
        nullif(trim(product_name), '') as product_name,

        cast(cast(case when trim(quantity) ~ '^[0-9]+(\.[0-9]+)?$'
             then trim(quantity) end as numeric)as integer) as quantity,

        cast(case 
        when trim(price) ~ '^-?[0-9]+(\.[0-9]+)?$' then cast(trim(price) as numeric(12,2)) 
        when lower(trim(price)) = 'two hundred' then 200
        end as numeric(12,2)) as price,

        cast(case
            when trim(tax) ~ '^-?[0-9]+(\.[0-9]+)?$' then cast(trim(tax)as numeric(12,2))
            when lower(trim(tax)) = 'fifteen' then 15
        end as numeric(12,2)) as tax,
        transaction_id as transaction_id_raw,
        transaction_date as transaction_date_raw,
        product_id as product_id_raw,
        price as price_raw,
        tax as tax_raw,

        array_remove(array[
            case when transaction_id ~ '[^0-9]' then 'transaction_id_prefix_removed' end,
            case when product_id ~ '[^0-9]' then 'product_id_prefix_removed' end,
            case when transaction_date ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' then 'date_format_ddmmyyyy' end,
            case when price ~ '[A-Za-z]' then 'price_from_words' end,
            case when tax   ~ '[A-Za-z]' then 'tax_from_words' end
        ], null) as fixed_values,
        _ting, _lsrcfil, _lotid

    from source
)

select *,
 array_remove(array[
        case when customer_id is null then 'missing_customer_id' end,
        case when quantity is null then 'missing_quantity' end,
        case when price is null then 'invalid_price' end,
        case when tax is null then 'invalid_tax' end,
        case when transaction_date is null then 'invalid_date' end
    ], null) as pending_values,
    (customer_id is not null and quantity is not null and price is not null
    and tax is not null and transaction_date is not null) as is_valid
from cleaned
