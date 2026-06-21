"""
load_to_db.py
-----------------
Loads transaction + prediction data into a SQL database (SQLite for now,
swappable to AWS RDS/PostgreSQL later via the same SQLAlchemy connection string).
"""

import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = "sqlite:///data/transactions.db"
INPUT_PATH = "data/transactions_with_predictions.csv"


def load_csv():
    return pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])


def load_to_sql(df, engine):
    db_df = df[[
        "transaction_id", "account_id", "timestamp", "amount",
        "merchant_category", "city", "amount_zscore",
        "is_unusual_city", "is_odd_hour", "predicted_anomaly", "is_synthetic_anomaly"
    ]].copy()

    db_df.to_sql("transactions", engine, if_exists="replace", index=False)
    print(f"Loaded {len(db_df)} rows into 'transactions' table.")


def run_sample_queries(engine):
    queries = {
        "Total flagged anomalies": """
            SELECT COUNT(*) as flagged_count
            FROM transactions
            WHERE predicted_anomaly = 1;
        """,
        "Top 5 riskiest accounts by total flagged amount": """
            SELECT account_id, SUM(amount) as total_flagged_amount, COUNT(*) as num_flagged
            FROM transactions
            WHERE predicted_anomaly = 1
            GROUP BY account_id
            ORDER BY total_flagged_amount DESC
            LIMIT 5;
        """,
        "Flagged transactions by city": """
            SELECT city, COUNT(*) as flagged_count
            FROM transactions
            WHERE predicted_anomaly = 1
            GROUP BY city
            ORDER BY flagged_count DESC;
        """,
        "Average transaction amount: flagged vs normal": """
            SELECT predicted_anomaly, AVG(amount) as avg_amount, COUNT(*) as count
            FROM transactions
            GROUP BY predicted_anomaly;
        """
    }

    with engine.connect() as conn:
        for label, query in queries.items():
            print(f"\n--- {label} ---")
            result = conn.execute(text(query))
            for row in result:
                print(row)


if __name__ == "__main__":
    print("Loading CSV...")
    df = load_csv()

    print("Connecting to database...")
    engine = create_engine(DB_PATH)

    print("Loading data into SQL table...")
    load_to_sql(df, engine)

    print("\nRunning sample SQL queries...")
    run_sample_queries(engine)
    