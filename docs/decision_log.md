## Decision: Schema-aware calendar validation

### Issue

The Singapore calendar dataset does not contain all fields commonly found
in other Inside Airbnb calendar datasets, including the daily price field.

### Decision

Calendar validation rules are applied conditionally based on the columns
available in the source dataset.

### Reason

A configurable pipeline should handle legitimate schema differences without
failing because an optional field is absent.

### Trade-off

Daily pricing analysis cannot be completed for this dataset snapshot.

## Decision: Use a dimensional star schema in DuckDB

### Options considered

1. Keep the datasets as independent Parquet files.
2. Create a fully normalised transactional schema.
3. Create a dimensional analytical model.

### Decision

A star schema was implemented in DuckDB using listing, host,
neighbourhood, and date dimensions with listing snapshot, calendar,
and review fact tables.

### Reason

The model supports simple analytical joins, reusable dimensions,
clear table grains, and efficient aggregation for reporting and
dashboard use.

DuckDB was selected because the project is local, analytical, and
Parquet-based. It provides SQL querying without requiring a separate
database server.

### Trade-off

The model contains some denormalised attributes and is designed for
analysis rather than transactional updates.

## Decision: Limit extreme prices only in selected visualisations

### Issue

The listing price distribution contains a small number of very high values
that reduce the readability of charts.

### Decision

Selected price charts are displayed only up to the 99th percentile. The
underlying records are not removed from the cleaned or analytical datasets.

### Reason

This improves visual readability while preserving source data and allowing
full-distribution summary statistics to remain available.

### Trade-off

The visualisations do not display the full upper price range. Chart titles
and captions clearly disclose this limitation.

## Decision: Use non-parametric hypothesis tests

### Options considered

1. Independent-samples t-tests
2. Parametric analysis after transforming prices
3. Mann-Whitney U tests

### Decision

Mann-Whitney U tests were used for the selected two-group comparisons.

### Reason

Listing prices were skewed and contained extreme values. Review ratings were
bounded and concentrated near the upper end of the scale. The non-parametric
test avoids relying on normally distributed outcomes.

Rank-biserial correlations were reported as effect sizes. Bootstrap
confidence intervals were calculated for median differences.

The Holm method was used to adjust p-values across the three tests.

### Trade-off

The Mann-Whitney U test compares distributions and does not directly estimate
a causal effect. When group distribution shapes differ, the result should not
be interpreted solely as a difference in medians.