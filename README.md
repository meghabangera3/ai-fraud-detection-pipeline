# AI-Powered Fraud Detection Pipeline

An automated, end-to-end ETL pipeline that simulates daily bank transaction data, detects anomalous/fraudulent transactions using an unsupervised machine learning model, stores results in a SQL database, and backs up outputs to AWS S3.

## Overview

This project simulates a real-world banking fraud detection workflow:

1. **Generate** ~50,000 synthetic daily transactions across 2,000 simulated accounts
2. **Engineer features** that capture how unusual a transaction is relative to an account's own behavior (amount deviation, odd hours, unusual location)
3. **Detect anomalies** using an Isolation Forest model (unsupervised — no labeled fraud data required)
4. **Generate a daily report** (CSV + plain-text summary) replacing manual review work
5. **Load results into SQL** (SQLite locally, swappable to AWS RDS/PostgreSQL) for queryable analytics
6. **Back up outputs to AWS S3** for durability and remote access

## Results

On synthetic data with a known ~2% anomaly rate (975 of 50,000 transactions):

| Metric | Value |
|---|---|
| Precision | 69.4% |
| Recall | 71.2% |
| Pipeline runtime (end-to-end) | ~8-17 seconds |

## Tech Stack

- **Python**: pandas, scikit-learn, Faker, SQLAlchemy, boto3
- **ML**: Isolation Forest (unsupervised anomaly detection)
- **Database**: SQLite (local), designed for AWS RDS PostgreSQL migration
- **Cloud**: AWS S3 (programmatic upload via boto3), IAM (least-privilege user)

## Project Structure