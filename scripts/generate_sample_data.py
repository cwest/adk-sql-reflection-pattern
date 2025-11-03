# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

# Initialize Faker
fake = Faker()

# Constants from PRD
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_TRANSACTIONS = 10000
NUM_FEEDBACK = 3000
OUTPUT_DIR = "data"


def generate_customers(num_customers):
    """Generates a DataFrame of customer data."""
    data = {
        "cust_id": [fake.uuid4() for _ in range(num_customers)],
        "first_name": [fake.first_name() for _ in range(num_customers)],
        "last_name": [fake.last_name() for _ in range(num_customers)],
        "email": [fake.email() for _ in range(num_customers)],
        "signup_dt": [
            fake.date_between(start_date="-2y", end_date="today")
            for _ in range(num_customers)
        ],
    }
    return pd.DataFrame(data)


def generate_products(num_products):
    """Generates a DataFrame of product data."""
    categories = [
        "Electronics",
        "Clothing",
        "Home Goods",
        "Books",
        "Sporting Goods",
        "Toys",
        "Garden",
        "Automotive",
    ]
    data = {
        "product_id": [fake.uuid4() for _ in range(num_products)],
        "product_name": [fake.word().capitalize() for _ in range(num_products)],
        "category": [random.choice(categories) for _ in range(num_products)],
        "unit_cst": [
            round(random.uniform(5.0, 500.0), 2) for _ in range(num_products)
        ],
    }
    return pd.DataFrame(data)


def generate_transactions(num_transactions, customers_df, products_df):
    """Generates a DataFrame of transaction data."""
    cust_ids = customers_df["cust_id"].tolist()
    prod_ids = products_df["product_id"].tolist()
    data = {
        "txn_id": [fake.uuid4() for _ in range(num_transactions)],
        "cust_id": [random.choice(cust_ids) for _ in range(num_transactions)],
        "product_id": [random.choice(prod_ids) for _ in range(num_transactions)],
        "txn_ts": [
            fake.date_time_between(start_date="-1y", end_date="now")
            for _ in range(num_transactions)
        ],
        "sale_amount": [
            round(random.uniform(10.0, 1000.0), 2) for _ in range(num_transactions)
        ],
        "refund_amount": [
            round(random.uniform(0.0, 100.0), 2) if random.random() < 0.2 else 0.0
            for _ in range(num_transactions)
        ],
    }
    return pd.DataFrame(data)


def generate_feedback(num_feedback, customers_df):
    """Generates a DataFrame of customer feedback data."""
    cust_ids = customers_df["cust_id"].tolist()
    data = {
        "feedback_id": [fake.uuid4() for _ in range(num_feedback)],
        "cust_id": [random.choice(cust_ids) for _ in range(num_feedback)],
        "rating": [random.randint(1, 5) for _ in range(num_feedback)],
    }
    return pd.DataFrame(data)


def main():
    """Main function to generate and save all data."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate data
    customers = generate_customers(NUM_CUSTOMERS)
    products = generate_products(NUM_PRODUCTS)
    transactions = generate_transactions(NUM_TRANSACTIONS, customers, products)
    feedback = generate_feedback(NUM_FEEDBACK, customers)

    # Save to CSV
    customers.to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
    products.to_csv(os.path.join(OUTPUT_DIR, "products.csv"), index=False)
    transactions.to_csv(os.path.join(OUTPUT_DIR, "transactions.csv"), index=False)
    feedback.to_csv(os.path.join(OUTPUT_DIR, "feedback.csv"), index=False)

    print(f"Sample data generated and saved in the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    main()
