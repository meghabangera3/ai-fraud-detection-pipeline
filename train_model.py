"""
train_model.py
-----------------
Loads raw transactions, engineers features, trains an Isolation Forest
to detect anomalous transactions, and evaluates against ground truth.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib

DATA_PATH = "data/transactions_raw.csv"
MODEL_PATH = "models/isolation_forest.pkl"


def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    return df


def engineer_features(df):
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour

    account_stats = df.groupby("account_id")["amount"].agg(["mean", "std"]).reset_index()
    account_stats.columns = ["account_id", "acc_avg_amount", "acc_std_amount"]
    account_stats["acc_std_amount"] = account_stats["acc_std_amount"].fillna(1)

    df = df.merge(account_stats, on="account_id", how="left")
    df["amount_zscore"] = (df["amount"] - df["acc_avg_amount"]) / df["acc_std_amount"]

    home_city = df.groupby("account_id")["city"].agg(lambda x: x.value_counts().idxmax()).reset_index()
    home_city.columns = ["account_id", "common_city"]
    df = df.merge(home_city, on="account_id", how="left")
    df["is_unusual_city"] = (df["city"] != df["common_city"]).astype(int)

    le = LabelEncoder()
    df["merchant_category_encoded"] = le.fit_transform(df["merchant_category"])

    df["is_odd_hour"] = df["hour"].apply(lambda h: 1 if h < 5 else 0)

    return df


def train_isolation_forest(df, contamination=0.02):
    features = ["amount", "amount_zscore", "is_unusual_city", "is_odd_hour", "merchant_category_encoded"]
    X = df[features]

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X)

    df["predicted_anomaly"] = model.predict(X) == -1

    joblib.dump(model, MODEL_PATH)
    return df, model, features


def evaluate(df):
    true_positives = ((df["predicted_anomaly"] == True) & (df["is_synthetic_anomaly"] == True)).sum()
    false_positives = ((df["predicted_anomaly"] == True) & (df["is_synthetic_anomaly"] == False)).sum()
    false_negatives = ((df["predicted_anomaly"] == False) & (df["is_synthetic_anomaly"] == True)).sum()
    total_actual_anomalies = df["is_synthetic_anomaly"].sum()
    total_flagged = df["predicted_anomaly"].sum()

    precision = true_positives / total_flagged if total_flagged > 0 else 0
    recall = true_positives / total_actual_anomalies if total_actual_anomalies > 0 else 0

    print("\n--- Model Evaluation ---")
    print(f"Total transactions: {len(df)}")
    print(f"Actual anomalies (ground truth): {total_actual_anomalies}")
    print(f"Flagged by model: {total_flagged}")
    print(f"True positives: {true_positives}")
    print(f"False positives: {false_positives}")
    print(f"False negatives: {false_negatives}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")


if __name__ == "__main__":
    print("Loading data...")
    df = load_data()

    print("Engineering features...")
    df = engineer_features(df)

    print("Training Isolation Forest model...")
    df, model, features = train_isolation_forest(df)

    evaluate(df)

    df.to_csv("data/transactions_with_predictions.csv", index=False)
    print("\nSaved results to data/transactions_with_predictions.csv")