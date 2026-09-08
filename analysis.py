import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "clinical_trial.db"
OUTPUT_DIR = ROOT / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

def get_frequency_table():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            c.sample,
            totals.total_count,
            c.population,
            c.count,
            100.0 * c.count / totals.total_count AS percentage
        FROM cell_counts c
        JOIN (
            SELECT
                sample,
                SUM(count) AS total_count
            FROM cell_counts
            GROUP BY sample
        ) totals
            ON c.sample = totals.sample
        ORDER BY c.sample, c.population
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def validate_frequency_table(df):
    if len(df) != 52500:
        raise ValueError(
            f"Expected 52500 rows, got {len(df)}"
        )

    percentage_sums = (
        df.groupby("sample")["percentage"].sum()
    )

    if not ((percentage_sums - 100).abs() < 1e-6).all():
        raise ValueError(
            "Percentages do not sum to 100 for every sample."
        )

if __name__ == "__main__":
    frequency_df = get_frequency_table()

    validate_frequency_table(frequency_df)

    frequency_df.to_csv(
        OUTPUT_DIR / "frequency_table.csv",
        index=False,
    )

    print(frequency_df.head(10))
    print("\nRows:", len(frequency_df))
    print("\nFrequency table created successfully.")