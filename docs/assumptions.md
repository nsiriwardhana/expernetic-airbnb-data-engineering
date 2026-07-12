## Calendar schema limitation

The Singapore calendar dataset dated 29 June 2026 does not include a daily
price column. Calendar validation and analysis are therefore limited to the
fields available in the source file.

Daily weekend-versus-weekday price analysis cannot be completed using this
calendar snapshot. Listing-level price from the listings dataset may still
be used for market price analysis.

## EDA limitations

Price visualisations may be limited to the 99th percentile for readability.
This is a display decision only. High-price records remain in the analytical
dataset.

Calendar unavailability is treated only as an estimated occupancy proxy.

The calendar file does not contain daily price fields. Weekend-versus-weekday
pricing and calendar-based revenue estimates are therefore not performed.

## Statistical analysis assumptions

Missing values were excluded separately for each hypothesis test.

The selected groups were mutually exclusive.

For the superhost comparison, listing ratings were aggregated to one average
rating per host to reduce repeated observations from hosts with multiple
listings.

Listing-level tests may still contain dependency because a host can control
more than one listing. A production analysis could use clustered standard
errors or hierarchical modelling.

Listings with exactly 10 reviews were included in the lower-review group.

Statistical significance was assessed using Holm-adjusted p-values at a
five-percent significance level.

Effect sizes and confidence intervals were considered alongside p-values.