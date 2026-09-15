#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

cp ../data/sales.csv      seeds/raw_sales.csv
cp ../data/costs.csv      seeds/raw_costs.csv
cp ../data/customers.csv  seeds/raw_customers.csv
cp ../data/products.csv   seeds/raw_products.csv
cp ../data/geography.csv  seeds/raw_geography.csv

dbt seed
echo "Seeds loaded. Run 'dbt run' next to build staging + marts."