import sqlite3
import pandas as pd

conn = sqlite3.connect("teiko.db")

query = """
    SELECT
        s.sample_id AS sample,
        cc.population,
        cc.count
    FROM cell_counts cc
    JOIN samples s ON cc.sample_id = s.sample_id
"""

raw_df = pd.read_sql_query(query, conn)
conn.close()

# Compute total count per sample
total_counts = raw_df.groupby("sample")["count"].sum().reset_index()
total_counts.rename(columns={"count": "total_count"}, inplace=True)
raw_df = raw_df.merge(total_counts, on="sample")

# Build clean dataframe explicitly
clean_df = pd.DataFrame()
clean_df["sample"] = raw_df["sample"].astype(str).str.strip()
clean_df["total_count"] = raw_df["total_count"].astype(int)
clean_df["population"] = raw_df["population"].astype(str).str.strip()
clean_df["count"] = raw_df["count"].astype(int)
clean_df["percentage"] = (raw_df["count"] / raw_df["total_count"] * 100).round(2)

# Remove duplicates and reset index
clean_df = clean_df.drop_duplicates()
clean_df = clean_df.reset_index(drop=True)

print(clean_df.head(10))
print(clean_df.info())