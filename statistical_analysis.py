import sqlite3
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from analysis import get_cell_frequency_summary

DB_PATH = "teiko.db"

#selecting data again like before
def get_sample_metadata():
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            s.sample_id AS sample,
            s.sample_type,
            sub.condition,
            sub.treatment,
            sub.response
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# function to filter data to melanoma PBMC patients on miraclib only
def get_filtered_data():
    
    summary = get_cell_frequency_summary()
    metadata = get_sample_metadata()

    # Merge frequency data with metadata on sample id
    df = summary.merge(metadata, on="sample")

    # Filter to melanoma, PBMC, miraclib only
    df = df[
        (df["condition"] == "melanoma") &
        (df["sample_type"] == "PBMC") &
        (df["treatment"] == "miraclib")
    ]

    return df

# stat analysis for cell populations, t test and U test
def run_statistical_analysis():

    df = get_filtered_data()

    populations = df["population"].unique()
    results = []

    for pop in populations:
        pop_df = df[df["population"] == pop]
        responders = pop_df[pop_df["response"] == "yes"]["percentage"]
        non_responders = pop_df[pop_df["response"] == "no"]["percentage"]

        # t test
        t_stat, t_pval = stats.ttest_ind(responders, non_responders)

        # Mann-Whitney U test
        u_stat, u_pval = stats.mannwhitneyu(responders, non_responders, alternative="two-sided")

        results.append({
            "population": pop,
            "t_statistic": round(t_stat, 4),
            "t_pvalue": round(t_pval, 4),
            "u_statistic": round(u_stat, 4),
            "u_pvalue": round(u_pval, 4),
            "significant_ttest": t_pval < 0.05,
            "significant_mannwhitney": u_pval < 0.05
        })

    return pd.DataFrame(results)

#boxplots
def plot_boxplots():
    
    df = get_filtered_data()

    populations = df["population"].unique()
    fig, axes = plt.subplots(1, len(populations), figsize=(18, 6))

    for ax, pop in zip(axes, populations):
        pop_df = df[df["population"] == pop]
        sns.boxplot(data=pop_df, x="response", y="percentage", ax=ax)
        ax.set_title(pop)
        ax.set_xlabel("Response")
        ax.set_ylabel("Relative Frequency (%)")

    plt.suptitle("Cell Population Frequencies: Responders vs Non-Responders", y=1.02)
    plt.tight_layout()
    plt.savefig("output_part3_boxplots.png", bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    results = run_statistical_analysis()
    print(results)
    plot_boxplots()
