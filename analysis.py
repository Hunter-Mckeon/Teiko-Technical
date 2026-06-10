import sqlite3
import pandas as pd

DB_PATH = "teiko.db"

# generate cell frequency by adding counts and dividing into percentages per sample
def get_cell_frequency_summary():
    
    conn = sqlite3.connect(DB_PATH)

    # Pull all cell counts joined with sample info
    query = """
    SELECT
        s.sample_id AS sample,
        cc.population,
        cc.count
    FROM cell_counts cc
    JOIN samples s ON cc.sample_id = s.sample_id
"""
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Compute total cell count per sample by summing all populations
    total_counts = df.groupby("sample")["count"].sum().reset_index()
    total_counts.rename(columns={"count": "total_count"}, inplace=True)

    # Merge totals back onto the main dataframe
    df = df.merge(total_counts, on="sample")

    # Calculate percentage
    df["percentage"] = (df["count"] / df["total_count"] * 100).round(2)

    # Reorder columns
    df = df[["sample", "total_count", "population", "count", "percentage"]]

    return df


if __name__ == "__main__":
    summary = get_cell_frequency_summary()
    summary.to_csv("output_part2_summary.csv", index=False)
    print(summary)
