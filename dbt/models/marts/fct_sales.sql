with sales as (
    select * from {{ ref('stg_sales') }}
),

costs as (
    select * from {{ ref('stg_costs') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

products as (
    select * from {{ ref('stg_products') }}
)

select
    s.order_id,
    s.order_date,
    s.order_year,
    s.quarter,
    s.customer_id,
    c.country,
    c.region,
    s.product_id,
    p.product_name,
    p.category,
    s.quantity,
    s.unit_price,
    s.revenue,
    co.material_cost,
    co.shipping_cost,
    co.total_cost,
    s.revenue - co.total_cost                                   as margin,
    round((s.revenue - co.total_cost) / nullif(s.revenue, 0), 4) as margin_pct
from sales s
left join costs     co on s.order_id    = co.order_id
left join customers c  on s.customer_id = c.customer_id
left join products  p  on s.product_id  = p.product_id
