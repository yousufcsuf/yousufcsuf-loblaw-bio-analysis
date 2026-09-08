import sqlite3
from pathlib import Path
from scipy.stats import mannwhitneyu
import plotly.express as px
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


def make_response_boxplot(response_df):
    fig = px.box(
        response_df,
        x="response",
        y="percentage",
        color="response",
        facet_col="population",
        facet_col_wrap=3,
        points=False,
        labels={
            "response": "Response",
            "percentage": "Relative frequency (%)",
            "population": "Cell population",
        },
        title="Miraclib Responders vs Non-Responders: Immune Cell Frequencies",
    )

    return fig

def get_response_frequency_data():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            f.sample,
            f.population,
            f.percentage,
            sub.response,
            s.time_from_treatment_start
        FROM (
            SELECT
                c.sample,
                c.population,
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
        ) f

        JOIN samples s
            ON f.sample = s.sample

        JOIN subjects sub
            ON s.project = sub.project
           AND s.subject = sub.subject

        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND sub.response IN ('yes', 'no')
    """

    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def run_statistical_analysis(response_df):
    results = []

    populations = sorted(response_df["population"].unique())

    for population in populations:
        subset = response_df[
            response_df["population"] == population
        ]

        responders = subset.loc[
            subset["response"] == "yes",
            "percentage",
        ]

        nonresponders = subset.loc[
            subset["response"] == "no",
            "percentage",
        ]

        statistic, p_value = mannwhitneyu(
            responders,
            nonresponders,
            alternative="two-sided",
        )

        results.append(
            {
                "population": population,
                "responder_n": len(responders),
                "nonresponder_n": len(nonresponders),
                "responder_median": responders.median(),
                "nonresponder_median": nonresponders.median(),
                "u_statistic": statistic,
                "p_value": p_value,
            }
        )

    results_df = pd.DataFrame(results)

    return results_df

def add_significance_columns(results_df):
    number_of_tests = len(results_df)

    results_df["bonferroni_p"] = (
        results_df["p_value"] * number_of_tests
    ).clip(upper=1.0)

    results_df["significant"] = (
        results_df["bonferroni_p"] < 0.05
    )

    return results_df


def get_baseline_cohort():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            s.sample,
            s.project,
            s.subject,
            s.sample_type,
            s.time_from_treatment_start,
            sub.condition,
            sub.age,
            sub.sex,
            sub.treatment,
            sub.response
        FROM samples s
        JOIN subjects sub
            ON s.project = sub.project
           AND s.subject = sub.subject
        WHERE sub.condition = 'melanoma'
          AND sub.treatment = 'miraclib'
          AND s.sample_type = 'PBMC'
          AND s.time_from_treatment_start = 0
    """

    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()

def summarize_baseline_cohort(baseline_df):
    samples_by_project = (
        baseline_df
        .groupby("project")["sample"]
        .nunique()
        .reset_index(name="sample_count")
    )

    subjects_by_response = (
        baseline_df
        .groupby("response")["subject"]
        .nunique()
        .reset_index(name="subject_count")
    )

    subjects_by_sex = (
        baseline_df
        .groupby("sex")["subject"]
        .nunique()
        .reset_index(name="subject_count")
    )

    return (
        samples_by_project,
        subjects_by_response,
        subjects_by_sex,
    )

def get_average_b_cells_melanoma_male_responders():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            ROUND(AVG(c.count), 2) AS average_b_cells
        FROM cell_counts c
        JOIN samples s
            ON c.sample = s.sample
        JOIN subjects sub
            ON s.project = sub.project
           AND s.subject = sub.subject
        WHERE c.population = 'b_cell'
          AND sub.condition = 'melanoma'
          AND sub.sex = 'M'
          AND sub.response = 'yes'
          AND s.time_from_treatment_start = 0
    """

    try:
        result = pd.read_sql_query(query, conn)
        return result.iloc[0]["average_b_cells"]
    finally:
        conn.close()

if __name__ == "__main__":
    frequency_df = get_frequency_table()
    validate_frequency_table(frequency_df)

    response_df = get_response_frequency_data()

    results_df = run_statistical_analysis(response_df)
    results_df = add_significance_columns(results_df)

    baseline_df = get_baseline_cohort()

    (
        samples_by_project,
        subjects_by_response,
        subjects_by_sex,
    ) = summarize_baseline_cohort(baseline_df)

    avg_b_cells = get_average_b_cells_melanoma_male_responders()

    baseline_df.to_csv(
        OUTPUT_DIR / "baseline_cohort.csv",
        index=False,
    )

    results_df.to_csv(
        OUTPUT_DIR / "statistical_results.csv",
        index=False,
    )

    print("\nBaseline cohort rows:")
    print(len(baseline_df))

    print("\nSamples by project:")
    print(samples_by_project)

    print("\nSubjects by response:")
    print(subjects_by_response)

    print("\nSubjects by sex:")
    print(subjects_by_sex)

    print("\nAverage B cells:")
    print(avg_b_cells)