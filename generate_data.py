"""
generate_data.py
-----------------
Generates synthetic daily bank/trading transaction data.
Simulates ~50K transactions/day, with ~2% deliberately anomalous
(unusual amount, odd hour, or unusual location) to mimic real-world fraud patterns.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_TRANSACTIONS = 50_000
NUM_ACCOUNTS = 2_000
ANOMALY_RATE = 0.02  # 2% of transactions will be "weird"

MERCHANT_CATEGORIES = [
    "Grocery", "Electronics", "Fuel", "Dining", "Travel",
    "Utilities", "Healthcare", "Entertainment", "Online Retail", "ATM Withdrawal"
]

CITIES = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata"]


def generate_account_pool(n=NUM_ACCOUNTS):
    """Create a pool of account IDs with a 'typical spending profile' each."""
    accounts = []
    for i in range(n):
        accounts.append({
            "account_id": f"ACC{i:05d}",
            "home_city": random.choice(CITIES),
            "avg_txn_amount": round(np.random.gamma(shape=2.0, scale=1500), 2)
        })
    return pd.DataFrame(accounts)


def generate_transactions(accounts_df, date, n=NUM_TRANSACTIONS):
    rows = []
    account_sample = accounts_df.sample(n=n, replace=True).reset_index(drop=True)

    for idx, acc in account_sample.iterrows():
        is_anomaly = random.random() < ANOMALY_RATE

        if not is_anomaly:
            amount = max(10, round(np.random.normal(acc["avg_txn_amount"], acc["avg_txn_amount"] * 0.3), 2))
            hour = random.randint(7, 22)
            city = acc["home_city"]
        else:
            anomaly_type = random.choice(["amount", "hour", "location"])
            amount = acc["avg_txn_amount"]
            hour = random.randint(7, 22)
            city = acc["home_city"]

            if anomaly_type == "amount":
                amount = round(acc["avg_txn_amount"] * random.uniform(8, 20), 2)
            elif anomaly_type == "hour":
                hour = random.choice([0, 1, 2, 3, 4])
            elif anomaly_type == "location":
                other_cities = [c for c in CITIES if c != acc["home_city"]]
                city = random.choice(other_cities)

        timestamp = date.replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )

        rows.append({
            "transaction_id": fake.uuid4(),
            "account_id": acc["account_id"],
            "timestamp": timestamp,
            "amount": amount,
            "merchant_category": random.choice(MERCHANT_CATEGORIES),
            "city": city,
            "is_synthetic_anomaly": is_anomaly
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("Generating account pool...")
    accounts_df = generate_account_pool()
    accounts_df.to_csv("data/accounts.csv", index=False)

    print(f"Generating {NUM_TRANSACTIONS} transactions for today...")
    today = datetime.now()
    transactions_df = generate_transactions(accounts_df, today)
    transactions_df.to_csv("data/transactions_raw.csv", index=False)

    print(f"Done. {len(transactions_df)} transactions saved.")
    print(f"Real anomaly count (ground truth): {transactions_df['is_synthetic_anomaly'].sum()}")
    print(transactions_df.head())