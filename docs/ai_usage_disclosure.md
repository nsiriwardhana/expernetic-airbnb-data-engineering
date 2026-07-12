# AI Usage Disclosure

## 1. Purpose

AI tools were used as development support during this assignment. They assisted with planning, code review, debugging, documentation, statistical-method selection, and presentation structure.

All AI-assisted outputs were reviewed, executed, tested, and modified before inclusion in the final submission. AI output was not accepted as correct without validation against the actual Singapore Inside Airbnb dataset.

## 2. AI Tools Used

| Tool | Model or Version | Purpose |
|---|---|---|
| ChatGPT | GPT-5.6 Thinking | Project planning, Python and SQL support, debugging, documentation, statistical-method review, dashboard refinement, and report structure |
| GitHub Copilot | Not used | Not applicable |
| Other AI tools | Not used | Not applicable |

Update this table before submission if any additional AI tools are used later.

## 3. AI-Assisted Sections

AI assistance was used in the following areas:

### Project planning

- selecting a one-city scope
- prioritising engineering depth over optional breadth
- defining the repository structure
- sequencing the work from profiling to reporting
- identifying mandatory and optional deliverables

### Data engineering

- drafting reusable cleaning functions
- reviewing price, percentage, Boolean, text, and date conversions
- designing the combined listing master
- separating critical validation failures from completeness warnings
- defining quarantine handling
- designing listing-level enrichment
- reviewing DuckDB star-schema logic
- drafting SQL analytical queries
- creating the master pipeline structure

### Debugging

AI support was used to diagnose and correct:

- missing PyArrow support for Parquet files
- schema differences in the Singapore calendar dataset
- pandas nullable Boolean compatibility with NumPy selection logic
- an overly strict missing-price validation rule
- Jupyter multiline assignment syntax
- Streamlit filter behaviour and p-value formatting
- an incorrect visual relationship in the first star-schema diagram

### Exploratory and statistical analysis

- selecting robust descriptive summaries
- using medians for skewed price data
- selecting Mann-Whitney U tests
- calculating rank-biserial effect sizes
- using bootstrap confidence intervals
- applying Holm correction for multiple tests
- improving business interpretations
- avoiding unsupported causal claims

### Dashboard and documentation

- organising Streamlit dashboard sections
- improving filter behaviour
- formatting statistical results
- structuring the README
- drafting assumptions, decisions, lineage, and limitations
- planning the final report structure

## 4. Candidate-Owned Work

The candidate remained responsible for:

- selecting the final project scope
- downloading the correct source files
- setting up the local development environment
- creating and maintaining the GitHub repository
- executing all Python, SQL, notebook, and dashboard code
- inspecting the actual dataset schemas
- reviewing all intermediate outputs
- identifying incorrect or unsuitable suggestions
- modifying code to match the real Singapore dataset
- interpreting the results
- preparing the final business conclusions
- verifying reproducibility
- deciding what to include and exclude from the final submission

## 5. Validation of AI-Generated Output

AI-assisted output was validated using the following methods:

### Code execution

All generated code was run in the project virtual environment. Errors were corrected before the code was retained.

### Data checks

Validation included:

- row-count comparison before and after transformations
- duplicate primary-key checks
- foreign-key and orphan-record checks
- schema inspection
- null-rate review
- value-range validation
- comparison of detailed and summary listing populations
- calendar coverage checks
- review coverage checks

### Database checks

The DuckDB model was checked for:

- duplicate listing keys
- duplicate host keys
- duplicate date keys
- orphan listing references
- orphan date references
- expected table counts

All implemented schema checks passed.

### Statistical checks

The statistical analysis was reviewed for:

- group definition
- sample size
- skewed distributions
- suitable non-parametric testing
- effect-size reporting
- confidence intervals
- multiple-testing correction
- practical interpretation
- avoidance of causal claims

### Reproducibility checks

The project was designed so that a reviewer can recreate the outputs using:

```bash
python -m pytest
python -m src.pipeline
python -m streamlit run dashboard/app.py
```

## 6. Meaningful Modifications Made

Several AI-generated suggestions required modification.

### Calendar schema handling

The first validation design assumed a `price` field existed in the calendar dataset. The Singapore calendar file did not contain this field. Validation rules were changed to be conditional on the columns that actually exist.

### Missing-price treatment

The first validation design treated missing listing prices as critical failures. This quarantined 505 listings. The logic was changed so missing prices are treated as completeness warnings, while negative prices remain critical failures.

### Host segmentation

The first implementation used `numpy.select()` with pandas nullable Boolean values, which caused a type error. The function was rewritten using pandas `.loc` assignments.

### Listing population

The detailed listings file contained 3,097 listings, while the summary file contained 3,247. A combined listing master was created so that the complete calendar-linked population was preserved.

### Streamlit filters

The first dashboard version selected every filter value by default, which made the sidebar crowded and contributed to confusing filtered totals. The logic was changed so blank selections represent all values.

### Statistical display

Very small adjusted p-values were displayed as long decimal values. The dashboard was updated to use scientific notation.

### Star-schema diagram

The first diagram incorrectly suggested a direct relationship from `dim_date` to `dim_listing`. This was removed so date keys connect only to the fact tables.

## 7. Suggestions Rejected or Not Used

The following suggestions were not adopted:

- multi-city processing, because the available time was better used on depth and quality
- weekend-versus-weekday price testing, because the calendar dataset lacked daily prices
- confirmed occupancy or revenue estimation, because calendar unavailability does not prove a booking
- aggressive removal of listings with missing analytical fields
- causal conclusions from statistical associations
- advanced machine learning, NLP, RAG, cloud deployment, and MLOps, because these were outside the prioritised scope

## 8. Critical Assessment of AI Use

AI was helpful for accelerating planning, drafting repetitive code, identifying possible validation rules, and improving documentation structure.

However, several outputs initially relied on assumptions that did not match the real dataset. This showed that AI-generated code must be treated as a draft rather than a trusted final result.

The most important safeguards were:

- inspecting real column names
- running every code path
- checking row counts
- reviewing data types
- testing business assumptions
- documenting limitations
- rejecting unsupported interpretations

## 9. Disclosure Summary

AI contributed to the development process, but the candidate retained ownership of all final decisions, execution, validation, interpretation, and submission quality.

A separate prompt appendix is provided in:

```text
docs/ai_prompts_appendix.md
```
