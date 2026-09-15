select
    order_id,
    cast(material_cost as double) as material_cost,
    cast(shipping_cost as double) as shipping_cost,
    cast(material_cost as double) + cast(shipping_cost as double) as total_cost
from {{ source('raw', 'raw_costs') }}