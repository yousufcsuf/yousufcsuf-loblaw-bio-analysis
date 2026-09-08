import sys
from pathlib import Path

# Add repository root to Python path so analysis.py can be imported
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis import (
    get_frequency_table,
    get_baseline_cohort,
    get_average_b_cells_melanoma_male_responders,
)


def test_frequency_table_row_count():
    df = get_frequency_table()

    assert len(df) == 52500


def test_percentages_sum_to_100():
    df = get_frequency_table()

    percentage_sums = (
        df.groupby("sample")["percentage"]
        .sum()
    )

    assert ((percentage_sums - 100).abs() < 1e-6).all()


def test_baseline_cohort_size():
    df = get_baseline_cohort()

    assert len(df) == 656


def test_baseline_cohort_filters():
    df = get_baseline_cohort()

    assert set(df["condition"]) == {"melanoma"}
    assert set(df["treatment"]) == {"miraclib"}
    assert set(df["sample_type"]) == {"PBMC"}
    assert set(df["time_from_treatment_start"]) == {0}


def test_average_b_cells():
    value = get_average_b_cells_melanoma_male_responders()

    assert round(float(value), 2) == 10206.15