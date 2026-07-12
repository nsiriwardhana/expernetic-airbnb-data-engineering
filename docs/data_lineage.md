## DuckDB analytical layer

### dim_listing

Source:
- listing_enriched.parquet

Transformations:
- Generate listing surrogate key
- Link host and neighbourhood dimensions
- Select descriptive listing attributes

### dim_host

Source:
- listing_enriched.parquet

Transformations:
- Group by natural host ID
- Select representative host attributes
- Generate host surrogate key

### dim_neighbourhood

Source:
- listing_enriched.parquet

Transformations:
- Extract distinct cleaned neighbourhood values
- Add city and country fields
- Generate neighbourhood surrogate key

### dim_date

Sources:
- calendar_valid.parquet
- reviews_detailed_valid.parquet
- listing_enriched.parquet

Transformations:
- Combine distinct dates
- Generate integer date key
- Derive year, quarter, month, day, and weekend fields

### fact_listing_snapshot

Source:
- listing_enriched.parquet

Transformations:
- Link listing and snapshot date keys
- Store listing-level analytical measures

### fact_calendar

Source:
- calendar_valid.parquet

Transformations:
- Link listing and date dimensions
- Retain daily availability and night restrictions

### fact_reviews

Source:
- reviews_detailed_valid.parquet

Transformations:
- Link listing and date dimensions
- Retain review identifiers and review-length measures

## Analytical SQL output layer

The DuckDB fact and dimension tables are queried through named SQL
analytical use cases.

Each query is stored in `sql/analysis_queries.sql` and executed using
`src/run_sql_analysis.py`.

Query outputs are exported to:

`outputs/tables/sql_analysis/`

Main analytical outputs include:

- Market overview
- Room-type comparison
- Neighbourhood comparison
- Host portfolio segmentation
- Host market concentration
- Superhost comparison
- Review-volume analysis
- Monthly review activity
- Monthly availability
- Minimum-night policies
- Source-data coverage

## Dashboard presentation layer

Source:
- DuckDB star schema
- Statistical results CSV
- Validation report CSV
- Completeness warning CSV

Application:
- dashboard/app.py

Outputs:
- Interactive market overview
- Market and neighbourhood analysis
- Host analysis
- Availability and review trends
- Geographic map
- Data-quality view