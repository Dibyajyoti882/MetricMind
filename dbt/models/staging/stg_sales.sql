with source as (
    select * from {{ source('raw', 'raw_sales') }}
)

select
    order_id,
    customer_id,
    product_id,
    cast(order_date as date)   as order_date,
    cast(quantity as integer)  as quantity,
    cast(unit_price as double) as unit_price,
    cast(revenue as double)    as revenue,
    quarter,
    date_part('year', cast(order_date as date)) as order_year
from source