# Analytical Data Model

## dim_host

Grain: One record per host

Primary key:
- host_key

Natural key:
- host_id

## dim_neighbourhood

Grain: One record per neighbourhood

Primary key:
- neighbourhood_key

Natural key:
- neighbourhood_name

## dim_listing

Grain: One record per listing

Primary key:
- listing_key

Natural key:
- listing_id

Foreign keys:
- host_key references dim_host.host_key
- neighbourhood_key references dim_neighbourhood.neighbourhood_key

## dim_date

Grain: One record per calendar date

Primary key:
- date_key

## fact_listing_snapshot

Grain: One record per listing for the dataset snapshot

Foreign keys:
- listing_key references dim_listing.listing_key
- snapshot_date_key references dim_date.date_key

## fact_calendar

Grain: One record per listing per calendar date

Logical composite key:
- listing_key
- date_key

Foreign keys:
- listing_key references dim_listing.listing_key
- date_key references dim_date.date_key

## fact_reviews

Grain: One record per detailed review

Natural key:
- review_id

Foreign keys:
- listing_key references dim_listing.listing_key
- date_key references dim_date.date_key