import sqlite3
import pandas as pd

DB_PATH = "teiko.db"

# Base query: melanoma PBMC samples at baseline treated with miraclib
BASE_QUERY = """
    SELECT
        s.sample_id,
        sub.project,
        sub.subject_id,
        sub.response,
        sub.sex
    FROM samples s
    JOIN subjects sub ON s.subject_id = sub.subject_id
    WHERE sub.condition = 'melanoma'
      AND s.sample_type = 'PBMC'
      AND sub.treatment = 'miraclib'
      AND s.time_from_treatment_start = 0
"""


def get_baseline_samples():
    """Return all melanoma PBMC baseline samples from miraclib patients."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(BASE_QUERY, conn)
    conn.close()
    return df


def samples_per_project(df):
    """Count number of samples from each project."""
    return df.groupby("project")["sample_id"].count().reset_index() \
             .rename(columns={"sample_id": "sample_count"})


def subjects_by_response(df):
    """Count unique subjects by responder/non-responder status."""
    return df.drop_duplicates("subject_id") \
             .groupby("response")["subject_id"].count().reset_index() \
             .rename(columns={"subject_id": "subject_count"})


def subjects_by_sex(df):
    """Count unique subjects by sex."""
    return df.drop_duplicates("subject_id") \
             .groupby("sex")["subject_id"].count().reset_index() \
             .rename(columns={"subject_id": "subject_count"})


def avg_bcell_male_responders():
    """Average b_cell count for male melanoma responders at time=0."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT ROUND(AVG(cc.count), 2) AS avg_b_cell
        FROM cell_counts cc
        JOIN samples s ON cc.sample_id = s.sample_id
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE sub.condition = 'melanoma'
          AND sub.sex = 'M'
          AND sub.response = 'yes'
          AND s.time_from_treatment_start = 0
          AND cc.population = 'b_cell'
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result["avg_b_cell"].iloc[0]


if __name__ == "__main__":
    df = get_baseline_samples()

    print("=== Samples per Project ===")
    print(samples_per_project(df))

    print("\n=== Subjects by Response ===")
    print(subjects_by_response(df))

    print("\n=== Subjects by Sex ===")
    print(subjects_by_sex(df))

    print("\n=== Avg B Cell Count (Male Melanoma Responders at Baseline) ===")
    print(avg_bcell_male_responders())
