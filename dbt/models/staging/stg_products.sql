select
    product_id,
    product_name,
    category,
    cast(list_price as double) as list_price
from {{ source('raw', 'raw_products') }}