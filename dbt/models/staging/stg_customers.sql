select
    c.customer_id,
    c.country,
    g.region
from {{ source('raw', 'raw_customers') }} c
left join {{ source('raw', 'raw_geography') }} g
    on c.country = g.country