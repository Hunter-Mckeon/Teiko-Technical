import sqlite3
import csv
import os

DB_PATH = "teiko.db"
CSV_PATH = "cell-count.csv"

CELL_POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

# build the database
def init_db(conn):
    
    cursor = conn.cursor()

    #subject table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id  TEXT PRIMARY KEY,
            project     TEXT NOT NULL,
            condition   TEXT,
            age         INTEGER,
            sex         TEXT,
            treatment   TEXT,
            response    TEXT
        )
    """)

    # samples table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            sample_id                   TEXT PRIMARY KEY,
            subject_id                  TEXT NOT NULL,
            sample_type                 TEXT,
            time_from_treatment_start   INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
        )
    """)

    # cell_counts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cell_counts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id   TEXT NOT NULL,
            population  TEXT NOT NULL,
            count       INTEGER NOT NULL,
            FOREIGN KEY (sample_id) REFERENCES samples (sample_id)
        )
    """)

    conn.commit()

# Read cell-count.csv and insert rows into the database.
def load_data(conn):
    cursor = conn.cursor()

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Insert subject but ignore if already exists (multiple samples per subject)
            cursor.execute("""
                INSERT OR IGNORE INTO subjects
                    (subject_id, project, condition, age, sex, treatment, response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["subject"],
                row["project"],
                row["condition"],
                int(row["age"]),
                row["sex"],
                row["treatment"],
                row["response"],
            ))

            # Insert sample
            cursor.execute("""
                INSERT OR IGNORE INTO samples
                    (sample_id, subject_id, sample_type, time_from_treatment_start)
                VALUES (?, ?, ?, ?)
            """, (
                row["sample"],
                row["subject"],
                row["sample_type"],
                int(row["time_from_treatment_start"]),
            ))

            # Insert one row per cell population
            for population in CELL_POPULATIONS:
                cursor.execute("""
                    INSERT INTO cell_counts (sample_id, population, count)
                    VALUES (?, ?, ?)
                """, (
                    row["sample"],
                    population,
                    int(row[population]),
                ))

    conn.commit()

# Make sure it's a fresh run each time to not get replicated data
if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)  

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    load_data(conn)
    conn.close()
    print(f"Database created: {DB_PATH}")
