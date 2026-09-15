"""
MetricMind — Mock Corporate Data Generator
Owner: Member 2 (Data Engineer)
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).parent

REGIONS = {
    "Europe": ["Germany", "France", "UK", "Spain", "Italy"],
    "North America": ["USA", "Canada"],
    "APAC": ["Japan", "Australia", "Singapore"],
}

PRODUCTS = [
    ("P-100", "Analytics Suite", "Software", 1200),
    ("P-101", "BI Connector", "Software", 400),
    ("P-102", "Data Pipeline Kit", "Hardware", 800),
    ("P-103", "Edge Sensor Pack", "Hardware", 250),
    ("P-104", "Support Plan", "Services", 150),
]

QUARTERS = {
    "Q1": (date(2025, 1, 1), date(2025, 3, 31)),
    "Q2": (date(2025, 4, 1), date(2025, 6, 30)),
    "Q3": (date(2025, 7, 1), date(2025, 9, 30)),
}


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def write_geography():
    with open(OUT / "geography.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "region"])
        for region, countries in REGIONS.items():
            for c in countries:
                w.writerow([c, region])


def write_products():
    with open(OUT / "products.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "product_name", "category", "list_price"])
        for row in PRODUCTS:
            w.writerow(row)


def write_customers(n=200):
    rows = []
    cid = 1
    for region, countries in REGIONS.items():
        for _ in range(n // len(sum(REGIONS.values(), []))):
            country = random.choice(countries)
            rows.append((f"C-{cid:04d}", country))
            cid += 1
    with open(OUT / "customers.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "country"])
        w.writerows(rows)
    return rows


def write_sales_and_costs(customers):
    sales_rows = []
    cost_rows = []
    order_id = 1

    for quarter, (start, end) in QUARTERS.items():
        for customer_id, country in customers:
            if random.random() > 0.6:
                continue
            n_orders = random.randint(1, 3)
            for _ in range(n_orders):
                product_id, _, _, list_price = random.choice(PRODUCTS)
                qty = random.randint(1, 20)
                order_date = random_date(start, end)
                unit_price = list_price * random.uniform(0.9, 1.05)
                revenue = round(unit_price * qty, 2)

                material_cost = round(revenue * random.uniform(0.35, 0.45), 2)

                is_europe = country in REGIONS["Europe"]
                if is_europe and quarter == "Q3":
                    shipping_rate = random.uniform(0.22, 0.30)
                else:
                    shipping_rate = random.uniform(0.08, 0.13)
                shipping_cost = round(revenue * shipping_rate, 2)

                sales_rows.append([
                    f"O-{order_id:05d}", customer_id, product_id,
                    order_date.isoformat(), qty, unit_price, revenue, quarter,
                ])
                cost_rows.append([
                    f"O-{order_id:05d}", material_cost, shipping_cost,
                ])
                order_id += 1

    with open(OUT / "sales.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "customer_id", "product_id", "order_date",
                    "quantity", "unit_price", "revenue", "quarter"])
        w.writerows(sales_rows)

    with open(OUT / "costs.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "material_cost", "shipping_cost"])
        w.writerows(cost_rows)

    print(f"Generated {len(sales_rows)} orders across {len(QUARTERS)} quarters.")


if __name__ == "__main__":
    write_geography()
    write_products()
    customer_rows = write_customers()
    write_sales_and_costs(customer_rows)
    print("Mock data written to:", OUT)