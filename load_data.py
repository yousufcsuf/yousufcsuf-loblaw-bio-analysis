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

def load_csv():
    return pd.read_csv(CSV_PATH)

def build_subjects(df):
    subjects = df[
        [
            "project",
            "subject",
            "condition",
            "age",
            "sex",
            "treatment",
            "response",
        ]
    ].drop_duplicates()

    return subjects

def build_samples(df):
    samples = df[
        [
            "sample",
            "project",
            "subject",
            "sample_type",
            "time_from_treatment_start",
        ]
    ].drop_duplicates()

    return samples

def build_cell_counts(df):
    cell_counts = df.melt(
        id_vars=["sample"],
        value_vars=CELL_COLUMNS,
        var_name="population",
        value_name="count",
    )

    return cell_counts

def create_schema(conn):
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("DROP TABLE IF EXISTS cell_counts")
    conn.execute("DROP TABLE IF EXISTS samples")
    conn.execute("DROP TABLE IF EXISTS subjects")

    conn.execute("""
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
    """)

    conn.execute("""
        CREATE TABLE samples (
            sample TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            subject TEXT NOT NULL,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            FOREIGN KEY (project, subject)
                REFERENCES subjects(project, subject)
        )
    """)

    conn.execute("""
        CREATE TABLE cell_counts (
            sample TEXT NOT NULL,
            population TEXT NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY (sample, population),
            FOREIGN KEY (sample)
                REFERENCES samples(sample)
        )
    """)

def load_tables(conn, subjects, samples, cell_counts):
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

def verify_database(conn):
    for table in ["subjects", "samples", "cell_counts"]:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table}: {count}")

def main():
    df = load_csv()

    subjects = build_subjects(df)
    samples = build_samples(df)
    cell_counts = build_cell_counts(df)
    
    conn = sqlite3.connect(DB_PATH)

    try:
        create_schema(conn)

        load_tables(
            conn,
            subjects,
            samples,
            cell_counts,
        )

        conn.commit()
        verify_database(conn)
        violations = conn.execute( "PRAGMA foreign_key_check").fetchall()

        print("Database created successfully.")
        print("Subjects:", len(subjects))
        print("Samples:", len(samples))
        print("Cell counts:", len(cell_counts))
        print("Foreign key violations:", violations)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

