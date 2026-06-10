# Teiko Clinical Trial Analysis

## How to Run

This project was built with Python 3.13. All dependencies are listed in `requirements.txt`.

### Setup
```bash
make setup
```

### Run the Pipeline
```bash
make pipeline
```

This will initialize the database, load the data, and generate all output tables and plots.

### Launch the Dashboard
```bash
make dashboard
```

This starts the local Streamlit server. Open your browser to the URL shown in the terminal.

---

## Database Schema

The data is split into three tables:

**`subjects`** stores one row per patient with subject-level information that does not change across samples: subject ID, project, condition, age, sex, treatment, and response.

**`samples`** stores one row per biological sample, linked to subjects via subject_id. It holds sample-level information including sample ID, sample type, and time from treatment start.

**`cell_counts`** stores one row per cell population per sample, meaning five rows per sample. It holds the population name and raw cell count.

### Why this design?

Separating subjects from samples avoids repeating patient-level data across every sample row. Unpivoting the five cell populations into long format in `cell_counts` makes filtering and aggregating by population straightforward in SQL.

### How it scales

With hundreds of projects and thousands of samples, this schema scales cleanly because subject and sample data are stored once and referenced by ID. Adding indexes on `subject_id`, `sample_id`, and `population` in `cell_counts` would keep queries fast at scale. New cell population types can be added as new rows without any schema changes, and new metadata fields can be added as columns to `subjects` or `samples` without affecting the rest of the schema.

---

## Code Structure

The project is split into separate scripts by purpose rather than written as one large program. This was a deliberate decision to ensure quality and correctness at each stage. Working in smaller focused files makes it significantly easier to isolate and debug issues. If something is not working correctly, it is much faster to identify whether the problem lives in the data loading, the frequency calculation, the statistical analysis, or the subset queries when each of those lives in its own file rather than being buried in a single script.

**`load_data.py`** initializes the SQLite database and loads `cell-count.csv` into the three tables. This runs first and everything else depends on it.

**`analysis.py`** contains the core frequency calculation logic. The main function is importable, meaning other scripts and the dashboard can call it directly without duplicating code.

**`statistical_analysis.py`** filters to the melanoma PBMC miraclib cohort, runs both a t-test and Mann-Whitney U test for each cell population comparing responders to non-responders, and generates boxplots. It imports from `analysis.py` rather than rewriting the same query.

**`subset_analysis.py`** handles the database queries for the baseline cohort breakdown and the average B cell calculation.

**`analysis.ipynb`** serves as the centralized output location. All tables and visualizations from Parts 2 through 4 are rendered here, so a reviewer who only wants to see the results does not need to run the full pipeline and wait for outputs to generate. They can open the notebook and view everything directly.

**`dashboard.py`** is the Streamlit app that makes all of the above results available interactively in a browser.

In a production setting with more time, I would create a separate git branch for each new section of the project and only merge into main once the code was tested and working correctly. This keeps the main branch clean and stable at all times, which matters in collaborative or sensitive environments where others may be depending on that code.

---

## Dashboard

[Clinical Trial Analysis Dashboard](https://howardmckeonteikoanalysis.streamlit.app/)

---

## Future Analyses

**Generalized Statistical Analysis Across Conditions and Treatments**

The subset analysis was built to be interactive, allowing users to filter by any combination of condition, sample type, and treatment. A natural extension of this would be to run the full statistical comparison between responders and non-responders across each of these subsets automatically and consolidate the results into a single output. This would help determine whether the significant difference observed in cd4_t_cell frequency within the miraclib melanoma cohort holds across other conditions and treatments, or whether it is specific to that group.

**Survival Analysis**

Statistical significance does not always reflect clinical value. A treatment that extends average patient survival by two to three years may not reach significance given the sample sizes typical in early trials, but that outcome is still enormously meaningful to patients. With longer term follow up data that includes survival outcomes, a survival analysis comparing responders and non-responders would give a more complete picture of how treatment response relates to overall patient benefit.

**BMI and Obesity as a Covariate**

Obesity is one of the leading contributors to mortality across many conditions. Including patient BMI in the dataset would allow for analysis of whether immune cell population distributions correlate with obesity status, and whether that relationship affects treatment response. If a correlation exists, it could inform clinical recommendations around pairing weight management interventions with primary treatment to improve patient outcomes.
