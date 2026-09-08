import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "cell-count.csv"
DB_PATH = ROOT / "clinical_trial.db"

CELL_COLUMNS = [
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
]


def create_schema(conn):
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("DROP TABLE IF EXISTS cell_counts")
    conn.execute("DROP TABLE IF EXISTS samples")
    conn.execute("DROP TABLE IF EXISTS subjects")

    conn.execute(
        """
        CREATE TABLE subjects (
            project TEXT NOT NULL,
            subject TEXT NOT NULL,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT,
            PRIMARY KEY (project, subject)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE samples (
            sample TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            subject TEXT NOT NULL,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            FOREIGN KEY (project, subject)
                REFERENCES subjects(project, subject)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE cell_counts (
            sample TEXT NOT NULL,
            population TEXT NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY (sample, population),
            FOREIGN KEY (sample)
                REFERENCES samples(sample)
        )
        """
    )


def prepare_tables(df):
    subjects = (
        df[
            [
                "project",
                "subject",
                "condition",
                "age",
                "sex",
                "treatment",
                "response",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    samples = (
        df[
            [
                "sample",
                "project",
                "subject",
                "sample_type",
                "time_from_treatment_start",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    cell_counts = df.melt(
        id_vars=["sample"],
        value_vars=CELL_COLUMNS,
        var_name="population",
        value_name="count",
    )

    return subjects, samples, cell_counts


def validate_data(df, subjects, samples, cell_counts):
    if samples["sample"].duplicated().any():
        raise ValueError("Duplicate sample IDs detected.")

    if cell_counts["count"].isna().any():
        raise ValueError("Missing cell counts detected.")

    if (cell_counts["count"] < 0).any():
        raise ValueError("Negative cell counts detected.")

    expected_rows = len(samples) * len(CELL_COLUMNS)

    if len(cell_counts) != expected_rows:
        raise ValueError("Unexpected cell-count row count.")

    print(f"CSV rows: {len(df)}")
    print(f"Subjects: {len(subjects)}")
    print(f"Samples: {len(samples)}")
    print(f"Cell measurements: {len(cell_counts)}")


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH.name} was not found."
        )

    df = pd.read_csv(CSV_PATH)

    subjects, samples, cell_counts = prepare_tables(df)

    validate_data(
        df,
        subjects,
        samples,
        cell_counts,
    )

    conn = sqlite3.connect(DB_PATH)

    try:
        create_schema(conn)

        subjects.to_sql(
            "subjects",
            conn,
            if_exists="append",
            index=False,
        )

        samples.to_sql(
            "samples",
            conn,
            if_exists="append",
            index=False,
        )

        cell_counts.to_sql(
            "cell_counts",
            conn,
            if_exists="append",
            index=False,
        )

        conn.commit()

        print(
            f"Database created successfully: {DB_PATH.name}"
        )

    finally:
        conn.close()


if __name__ == "__main__":
    main()