cube(`Sales`, {
  sql: `SELECT * FROM main.fct_sales`,

  measures: {
    count: { type: `count` },

    revenue: {
      sql: `revenue`,
      type: `sum`,
      title: `Revenue`,
      description: `Governed revenue = quantity * unit_price, computed once in dbt.`,
    },

    materialCost: { sql: `material_cost`, type: `sum`, title: `Material Cost` },
    shippingCost: { sql: `shipping_cost`, type: `sum`, title: `Shipping Cost` },
    totalCost: { sql: `total_cost`, type: `sum`, title: `Total Cost` },

    margin: {
      sql: `margin`,
      type: `sum`,
      title: `Margin`,
      description: `Governed margin = revenue - total_cost.`,
    },

    marginPct: {
      sql: `${margin} / NULLIF(${revenue}, 0)`,
      type: `number`,
      title: `Margin %`,
      format: `percent`,
    },
  },

  dimensions: {
    orderId: { sql: `order_id`, type: `string`, primaryKey: true },
    orderDate: { sql: `order_date`, type: `time` },
    quarter: { sql: `quarter`, type: `string` },
    region: { sql: `region`, type: `string`, title: `Geography: Region` },
    country: { sql: `country`, type: `string`, title: `Geography: Country` },
    productName: { sql: `product_name`, type: `string` },
    category: { sql: `category`, type: `string`, title: `Product: Category` },
  },
});
