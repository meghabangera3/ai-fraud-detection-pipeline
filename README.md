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
ai-fraud-pipeline/

├── generate_data.py        # Synthetic transaction data generator

├── train_model.py           # Feature engineering + Isolation Forest training/evaluation

├── generate_report.py       # Daily anomaly report generator

├── load_to_db.py             # SQL database loader + sample queries

├── upload_to_s3.py           # AWS S3 upload of reports/database backups

├── run_pipeline.py           # Master orchestration script (runs all steps)

├── data/                      # Generated CSVs and SQLite database

├── reports/                   # Daily generated reports

└── models/                    # Saved trained model
## How It Works

### 1. Data Generation
Simulates realistic transaction behavior: each account has a personal spending baseline, and ~2% of transactions are deliberately anomalous (unusual amount, odd hour, or different city than usual) — mimicking real fraud patterns.

### 2. Feature Engineering
Rather than using raw transaction amount, the model uses:
- **Z-score** of amount relative to the account's own historical average
- **Unusual city flag** (transaction location differs from account's typical city)
- **Odd hour flag** (transactions between midnight–5am)
- **Merchant category** (encoded)

### 3. Anomaly Detection
An Isolation Forest model is trained on these engineered features, learning to isolate outliers without needing labeled fraud examples — directly applicable to real-world fraud detection, where labeled data is scarce.

### 4. Reporting & Storage
Flagged transactions are summarized into a daily report and loaded into a SQL database, enabling queries like "top 5 riskiest accounts" or "flagged transactions by city" — replacing what would otherwise be manual spreadsheet review.

### 5. Cloud Backup
Daily reports and database snapshots are uploaded to AWS S3, demonstrating integration with cloud infrastructure for durability and remote accessibility.

## Running the Pipeline

\`\`\`bash
# Install dependencies
pip install pandas faker scikit-learn sqlalchemy boto3

# Run the full pipeline end-to-end
python run_pipeline.py

# Upload outputs to S3 (requires AWS credentials configured via `aws configure`)
python upload_to_s3.py
\`\`\`

## Future Improvements

- Migrate from SQLite to AWS RDS (PostgreSQL) for production-grade storage
- Deploy as an AWS Lambda function triggered daily via EventBridge for full automation
- Add a simple dashboard (Streamlit) for visualizing flagged transactions
- Experiment with supervised models if labeled fraud data becomes available, comparing performance against the unsupervised baseline