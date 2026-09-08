import streamlit as st

from analysis import (
    get_frequency_table,
    get_response_frequency_data,
    run_statistical_analysis,
    add_significance_columns,
    make_response_boxplot,
    get_baseline_cohort,
    summarize_baseline_cohort,
    get_average_b_cells_melanoma_male_responders,
)


st.set_page_config(
    page_title="Loblaw Bio Immune Cell Analysis",
    layout="wide",
)

st.title("Loblaw Bio Immune Cell Analysis")

st.write(
    "Interactive analysis of immune cell populations "
    "across clinical trial samples."
)


tab1, tab2, tab3 = st.tabs(
    [
        "Part 2 - Cell Frequencies",
        "Part 3 - Responder Analysis",
        "Part 4 - Baseline Cohort",
    ]
)


# ---------------------------------------------------------
# PART 2
# ---------------------------------------------------------

with tab1:
    st.header("Cell Population Frequencies")

    frequency_df = get_frequency_table()

    st.write(
        "For each sample, the relative frequency of each immune "
        "cell population is calculated as a percentage of the "
        "sample's total cell count."
    )

    sample_options = sorted(
        frequency_df["sample"].unique()
    )

    selected_sample = st.selectbox(
        "Select a sample",
        sample_options,
        key="sample_selector",
    )

    sample_df = frequency_df[
        frequency_df["sample"] == selected_sample
    ]

    st.subheader(
        f"Cell Frequencies for {selected_sample}"
    )

    st.dataframe(
        sample_df,
        use_container_width=True,
    )

    st.subheader("Complete Frequency Table")

    st.dataframe(
        frequency_df,
        use_container_width=True,
    )

    st.download_button(
        label="Download Frequency Table",
        data=frequency_df.to_csv(index=False),
        file_name="frequency_table.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------
# PART 3
# ---------------------------------------------------------

with tab2:
    st.header(
        "Miraclib Responders vs Non-Responders"
    )

    st.write(
        "This analysis compares immune-cell relative frequencies "
        "between responders and non-responders among melanoma "
        "patients treated with miraclib using PBMC samples."
    )

    response_df = get_response_frequency_data()

    results_df = run_statistical_analysis(
        response_df
    )

    results_df = add_significance_columns(
        results_df
    )

    fig = make_response_boxplot(
        response_df
    )

    st.subheader(
        "Responder vs Non-Responder Boxplots"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Statistical Results")

    st.dataframe(
        results_df,
        use_container_width=True,
    )

    significant_df = results_df[
        results_df["significant"]
    ]

    if significant_df.empty:
        st.info(
            "No immune-cell populations showed a statistically "
            "significant difference after Bonferroni correction."
        )
    else:
        st.success(
            "Statistically significant populations were detected."
        )

        st.dataframe(
            significant_df,
            use_container_width=True,
        )

    st.download_button(
        label="Download Statistical Results",
        data=results_df.to_csv(index=False),
        file_name="statistical_results.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------
# PART 4
# ---------------------------------------------------------

with tab3:
    st.header("Baseline Miraclib Cohort")

    st.write(
        "This cohort includes melanoma PBMC samples at baseline "
        "(time_from_treatment_start = 0) from patients treated "
        "with miraclib."
    )

    baseline_df = get_baseline_cohort()

    (
        samples_by_project,
        subjects_by_response,
        subjects_by_sex,
    ) = summarize_baseline_cohort(
        baseline_df
    )

    avg_b_cells = (
        get_average_b_cells_melanoma_male_responders()
    )

    # -------------------------
    # Summary metrics
    # -------------------------

    col1, col2, col3, col4 = st.columns(4)

    responder_row = subjects_by_response[
        subjects_by_response["response"] == "yes"
    ]

    nonresponder_row = subjects_by_response[
        subjects_by_response["response"] == "no"
    ]

    responder_count = (
        int(responder_row["subject_count"].iloc[0])
        if not responder_row.empty
        else 0
    )

    nonresponder_count = (
        int(nonresponder_row["subject_count"].iloc[0])
        if not nonresponder_row.empty
        else 0
    )

    with col1:
        st.metric(
            "Baseline Samples",
            len(baseline_df),
        )

    with col2:
        st.metric(
            "Responders",
            responder_count,
        )

    with col3:
        st.metric(
            "Non-Responders",
            nonresponder_count,
        )

    with col4:
        st.metric(
            "Average B Cells",
            f"{avg_b_cells:.2f}",
        )

    # -------------------------
    # Samples by project
    # -------------------------

    st.subheader("Samples by Project")

    st.dataframe(
        samples_by_project,
        use_container_width=True,
    )

    # -------------------------
    # Subjects by response
    # -------------------------

    st.subheader("Subjects by Response")

    st.dataframe(
        subjects_by_response,
        use_container_width=True,
    )

    # -------------------------
    # Subjects by sex
    # -------------------------

    st.subheader("Subjects by Sex")

    st.dataframe(
        subjects_by_sex,
        use_container_width=True,
    )

    # -------------------------
    # Special Part 4 answer
    # -------------------------

    st.subheader(
        "Average B Cells for Melanoma Male Responders at Baseline"
    )

    st.write(
        "This calculation includes melanoma male responders at "
        "time = 0 across all sample types and all treatment types."
    )

    st.metric(
        "Average B-cell Count",
        f"{avg_b_cells:.2f}",
    )

    # -------------------------
    # Baseline cohort table
    # -------------------------

    st.subheader("Baseline Cohort Data")

    st.dataframe(
        baseline_df,
        use_container_width=True,
    )

    st.download_button(
        label="Download Baseline Cohort",
        data=baseline_df.to_csv(index=False),
        file_name="baseline_cohort.csv",
        mime="text/csv",
    )