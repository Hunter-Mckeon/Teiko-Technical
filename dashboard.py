import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import pandas as pd
from analysis import get_cell_frequency_summary
from statistical_analysis import run_statistical_analysis, get_filtered_data
from subset_analysis import avg_bcell_male_responders

st.set_page_config(page_title="Clinical Trial Analysis", layout="wide")
st.title("Clinical Trial Immune Cell Analysis")

tab1, tab2, tab3 = st.tabs(["Cell Frequency Table", "Statistical Analysis", "Data Subset"])

# --- Tab 1: Cell Frequency Table ---
with tab1:
    st.header("Cell Population Frequency Summary")

    summary = get_cell_frequency_summary()

    col1, col2 = st.columns(2)
    with col1:
        selected_populations = st.multiselect(
            "Filter by Population",
            options=summary["population"].unique().tolist(),
            default=summary["population"].unique().tolist()
        )
    with col2:
        selected_samples = st.multiselect(
            "Filter by Sample",
            options=summary["sample"].unique().tolist(),
            default=[]
        )

    filtered = summary[summary["population"].isin(selected_populations)]
    if selected_samples:
        filtered = filtered[filtered["sample"].isin(selected_samples)]

    st.dataframe(filtered, use_container_width=True)


# --- Tab 2: Statistical Analysis ---
with tab2:
    st.header("Responders vs Non-Responders")
    st.caption("Melanoma PBMC patients treated with miraclib")

    st.subheader("Statistical Results")
    results = run_statistical_analysis()
    st.dataframe(results, use_container_width=True)

    st.subheader("Boxplots by Cell Population")
    df = get_filtered_data()
    populations = df["population"].unique()
    fig, axes = plt.subplots(1, len(populations), figsize=(18, 6))
    for ax, pop in zip(axes, populations):
        pop_df = df[df["population"] == pop]
        sns.boxplot(data=pop_df, x="response", y="percentage", ax=ax)
        ax.set_title(pop)
        ax.set_xlabel("Response")
        ax.set_ylabel("Relative Frequency (%)")
    plt.tight_layout()
    st.pyplot(fig)


# --- Tab 3: Data Subset ---
with tab3:
    st.header("Data Subset Analysis")

    DB_PATH = "teiko.db"

    conn = sqlite3.connect(DB_PATH)
    conditions = pd.read_sql_query("SELECT DISTINCT condition FROM subjects", conn)["condition"].tolist()
    sample_types = pd.read_sql_query("SELECT DISTINCT sample_type FROM samples", conn)["sample_type"].tolist()
    treatments = pd.read_sql_query("SELECT DISTINCT treatment FROM subjects", conn)["treatment"].tolist()
    time_points = pd.read_sql_query("SELECT DISTINCT time_from_treatment_start FROM samples ORDER BY time_from_treatment_start", conn)["time_from_treatment_start"].tolist()
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        condition = st.selectbox("Condition", conditions, index=conditions.index("melanoma"))
    with col2:
        sample_type = st.selectbox("Sample Type", sample_types, index=sample_types.index("PBMC"))
    with col3:
        treatment = st.selectbox("Treatment", treatments, index=treatments.index("miraclib"))
    with col4:
        time_point = st.selectbox("Time from Treatment Start", time_points, index=time_points.index(0))

    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT
            s.sample_id,
            sub.project,
            sub.subject_id,
            sub.response,
            sub.sex
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE sub.condition = '{condition}'
          AND s.sample_type = '{sample_type}'
          AND sub.treatment = '{treatment}'
          AND s.time_from_treatment_start = {time_point}
    """
    df_subset = pd.read_sql_query(query, conn)
    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Samples per Project")
        st.dataframe(
            df_subset.groupby("project")["sample_id"].count().reset_index()
                     .rename(columns={"sample_id": "sample_count"}),
            use_container_width=True
        )
    with col2:
        st.subheader("Subjects by Response")
        st.dataframe(
            df_subset.drop_duplicates("subject_id").groupby("response")["subject_id"].count().reset_index()
                     .rename(columns={"subject_id": "subject_count"}),
            use_container_width=True
        )
    with col3:
        st.subheader("Subjects by Sex")
        st.dataframe(
            df_subset.drop_duplicates("subject_id").groupby("sex")["subject_id"].count().reset_index()
                     .rename(columns={"subject_id": "subject_count"}),
            use_container_width=True
        )

    st.subheader("Avg B Cell Count: Male Melanoma Responders at Baseline")
    st.metric(label="Average B Cell Count", value=avg_bcell_male_responders())
