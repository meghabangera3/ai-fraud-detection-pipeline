"""
run_pipeline.py
-----------------
Master orchestration script. Runs the full pipeline end-to-end:
1. Generate daily transaction data
2. Engineer features + train/run anomaly detection model
3. Generate daily report
4. Load results into SQL database
"""

import time
import sys
from datetime import datetime

import generate_data
import train_model
import generate_report
import load_to_db


def run_pipeline():
    start_time = time.time()
    print("=" * 60)
    print(f"PIPELINE RUN STARTED — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        print("\n[1/4] Generating transaction data...")
        accounts_df = generate_data.generate_account_pool()
        accounts_df.to_csv("data/accounts.csv", index=False)
        transactions_df = generate_data.generate_transactions(accounts_df, datetime.now())
        transactions_df.to_csv("data/transactions_raw.csv", index=False)
        print(f"    -> {len(transactions_df)} transactions generated.")

        print("\n[2/4] Training model and detecting anomalies...")
        df = train_model.load_data()
        df = train_model.engineer_features(df)
        df, model, features = train_model.train_isolation_forest(df)
        train_model.evaluate(df)
        df.to_csv("data/transactions_with_predictions.csv", index=False)

        print("\n[3/4] Generating daily report...")
        summary_text, csv_path, txt_path = generate_report.generate_report(df)
        print(f"    -> Report saved to {csv_path} and {txt_path}")

        print("\n[4/4] Loading results into SQL database...")
        from sqlalchemy import create_engine
        engine = create_engine(load_to_db.DB_PATH)
        load_to_db.load_to_sql(df, engine)

        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"PIPELINE RUN COMPLETED SUCCESSFULLY in {elapsed:.2f} seconds")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nPIPELINE FAILED: {e}")
        return False


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)