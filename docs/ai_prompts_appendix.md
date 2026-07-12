# AI Prompt Appendix

The prompts below are representative of the main AI-assisted tasks completed during the project. Some were refined through follow-up conversation.

## Prompt 1: Assignment planning

> Review this Data Engineer Intern assignment and create an A-to-Z execution plan that can be completed before the deadline. Prioritise depth, engineering quality, reproducibility, and clear documentation.

## Prompt 2: Repository structure

> Suggest a professional folder structure for a reproducible Airbnb data engineering project using Python, pandas, Parquet, DuckDB, SQL, Jupyter, Streamlit, and pytest.

## Prompt 3: Dataset profiling

> Create reusable Python code to profile each dataset, including row counts, column counts, data types, null counts, null percentages, unique counts, duplicates, ranges, and sample values.

## Prompt 4: File relationship analysis

> Help me compare detailed listings, summary listings, calendar, and reviews. Identify primary keys, foreign keys, summary-only listings, and apparent duplicate review records.

## Prompt 5: Cleaning functions

> Draft reusable Python functions to clean currency values, percentages, Boolean fields, dates, identifiers, numeric columns, and text fields while preserving missing values.

## Prompt 6: Combined listing master

> Design a method to combine detailed and summary listings. Detailed records should take priority, while summary-only listings should be retained with explicit nulls for unavailable detailed fields.

## Prompt 7: Validation framework

> Create a rule-based validation framework that separates valid and invalid records, records failed rules, exports a validation report, and quarantines critical failures without silent deletion.

## Prompt 8: Schema-aware validation

> The Singapore calendar dataset does not contain a price column. Update the validation logic so optional rules are applied only when the required columns exist.

## Prompt 9: Enrichment

> Create listing-level calendar and review summaries, derive occupancy proxy, host tenure, host portfolio segment, review frequency, price per bedroom, and neighbourhood aggregates.

## Prompt 10: DuckDB model

> Design and implement a DuckDB star schema with host, listing, neighbourhood, and date dimensions plus listing snapshot, calendar, and review fact tables. Include schema checks.

## Prompt 11: Analytical SQL

> Write named SQL queries for market overview, room types, neighbourhoods, host concentration, superhost comparison, review activity, availability, minimum-night policies, and source coverage.

## Prompt 12: Exploratory analysis

> Create an EDA plan with high-quality charts and a plain-English business interpretation for every finding. Preserve outliers in the dataset and limit only selected charts for readability.

## Prompt 13: Statistical analysis

> Recommend suitable tests for skewed Airbnb price and rating data. Include null and alternative hypotheses, assumptions, effect sizes, confidence intervals, multiple-testing correction, and business interpretation.

## Prompt 14: Dashboard

> Build a Streamlit dashboard backed by DuckDB with filters, KPIs, room-type analysis, neighbourhood analysis, host analysis, availability trends, review trends, a map, statistical findings, and data-quality views.

## Prompt 15: Dashboard refinement

> Update the dashboard so blank multiselect filters mean all values, add a reset button, show the full listing count clearly, and format very small p-values in scientific notation.

## Prompt 16: Automated tests

> Create pytest tests for cleaning, validation, host segmentation, calendar aggregation, review aggregation, and listing-master construction.

## Prompt 17: Master pipeline

> Create one Python command that runs cleaning, validation, enrichment, DuckDB construction, and analytical SQL with logging, timing, and error handling.

## Prompt 18: Architecture documentation

> Create a data architecture diagram and a star-schema diagram that can be used in the README and final report.

## Prompt 19: README

> Rewrite the README so it includes project scope, dataset details, setup, execution commands, architecture, data model, tests, dashboard instructions, assumptions, limitations, outputs, and reproducibility.

## Prompt 20: AI disclosure

> Draft a transparent AI usage disclosure listing assisted sections, validation methods, meaningful modifications, rejected suggestions, and critical assessment.
