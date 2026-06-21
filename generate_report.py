"""
generate_report.py
-----------------
Takes model predictions and generates a clean daily anomaly report —
this is the piece that replaces manual review/reporting work.
"""

import pandas as pd
from datetime import datetime

INPUT_PATH = "data/transactions_with_predictions.csv"
REPORT_CSV_PATH = "reports/flagged_transactions_{date}.csv"
REPORT_TXT_PATH = "reports/summary_{date}.txt"


def load_predictions():
    return pd.read_csv(INPUT_PATH, parse_dates=["timestamp"])


def generate_report(df):
    today_str = datetime.now().strftime("%Y-%m-%d")

    flagged = df[df["predicted_anomaly"] == True].copy()
    flagged = flagged.sort_values("amount", ascending=False)

    csv_path = REPORT_CSV_PATH.format(date=today_str)
    flagged[["transaction_id", "account_id", "timestamp", "amount",
             "merchant_category", "city", "is_unusual_city", "is_odd_hour"]].to_csv(csv_path, index=False)

    total_txns = len(df)
    total_flagged = len(flagged)
    pct_flagged = (total_flagged / total_txns) * 100

    top_categories = flagged["merchant_category"].value_counts().head(3)
    top_cities = flagged["city"].value_counts().head(3)
    top_accounts = flagged.groupby("account_id")["amount"].sum().sort_values(ascending=False).head(5)

    summary_lines = [
        f"DAILY ANOMALY DETECTION REPORT — {today_str}",
        "=" * 50,
        f"Total transactions processed: {total_txns:,}",
        f"Flagged as anomalous: {total_flagged:,} ({pct_flagged:.2f}%)",
        "",
        "Top flagged merchant categories:",
    ]
    for cat, count in top_categories.items():
        summary_lines.append(f"  - {cat}: {count}")

    summary_lines.append("")
    summary_lines.append("Top cities with flagged activity:")
    for city, count in top_cities.items():
        summary_lines.append(f"  - {city}: {count}")

    summary_lines.append("")
    summary_lines.append("Top 5 accounts by flagged transaction value:")
    for acc, total in top_accounts.items():
        summary_lines.append(f"  - {acc}: Rs {total:,.2f}")

    summary_lines.append("")
    summary_lines.append(f"Full detail saved to: {csv_path}")

    summary_text = "\n".join(summary_lines)

    txt_path = REPORT_TXT_PATH.format(date=today_str)
    with open(txt_path, "w") as f:
        f.write(summary_text)

    return summary_text, csv_path, txt_path


if __name__ == "__main__":
    print("Loading model predictions...")
    df = load_predictions()

    print("Generating report...\n")
    summary_text, csv_path, txt_path = generate_report(df)

    print(summary_text)
    print(f"\nReport files saved:\n  - {csv_path}\n  - {txt_path}")