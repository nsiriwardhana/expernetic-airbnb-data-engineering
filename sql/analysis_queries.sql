-- QUERY: market_overview
SELECT
    COUNT(DISTINCT listings.listing_key) AS total_listings,
    COUNT(DISTINCT listings.host_key) AS total_hosts,
    COUNT(
        DISTINCT listings.neighbourhood_key
    ) AS total_neighbourhoods,
    ROUND(
        MEDIAN(facts.price),
        2
    ) AS median_listing_price,
    ROUND(
        AVG(facts.price),
        2
    ) AS average_listing_price,
    ROUND(
        AVG(facts.review_scores_rating),
        2
    ) AS average_review_rating,
    ROUND(
        AVG(
            facts.estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage
FROM fact_listing_snapshot AS facts
INNER JOIN dim_listing AS listings
    ON facts.listing_key = listings.listing_key;


-- QUERY: room_type_performance
SELECT
    listings.room_type,
    COUNT(*) AS listing_count,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS listing_share_percentage,
    ROUND(
        MEDIAN(facts.price),
        2
    ) AS median_price,
    ROUND(
        AVG(facts.price),
        2
    ) AS average_price,
    ROUND(
        AVG(facts.review_scores_rating),
        2
    ) AS average_rating,
    ROUND(
        AVG(
            facts.estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage
FROM dim_listing AS listings
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
GROUP BY listings.room_type
ORDER BY listing_count DESC;


-- QUERY: neighbourhood_market_summary
SELECT
    neighbourhoods.neighbourhood_name,
    COUNT(*) AS listing_count,
    COUNT(
        DISTINCT listings.host_key
    ) AS unique_host_count,
    ROUND(
        MEDIAN(facts.price),
        2
    ) AS median_price,
    ROUND(
        AVG(facts.price),
        2
    ) AS average_price,
    ROUND(
        AVG(facts.review_scores_rating),
        2
    ) AS average_rating,
    ROUND(
        AVG(
            facts.estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage,
    ROUND(
        SUM(
            CASE
                WHEN listings.room_type
                    = 'Entire home/apt'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS entire_home_share_percentage
FROM dim_listing AS listings
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
INNER JOIN dim_neighbourhood AS neighbourhoods
    ON listings.neighbourhood_key
        = neighbourhoods.neighbourhood_key
GROUP BY neighbourhoods.neighbourhood_name
HAVING COUNT(*) >= 10
ORDER BY median_price DESC NULLS LAST;


-- QUERY: host_segment_summary
SELECT
    COALESCE(
        hosts.host_segment,
        'Unknown'
    ) AS host_segment,
    COUNT(
        DISTINCT hosts.host_key
    ) AS host_count,
    COUNT(*) AS listing_count,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS listing_share_percentage,
    ROUND(
        MEDIAN(facts.price),
        2
    ) AS median_price,
    ROUND(
        AVG(facts.review_scores_rating),
        2
    ) AS average_rating,
    ROUND(
        AVG(
            facts.estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage
FROM dim_listing AS listings
LEFT JOIN dim_host AS hosts
    ON listings.host_key = hosts.host_key
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
GROUP BY
    COALESCE(
        hosts.host_segment,
        'Unknown'
    )
ORDER BY listing_count DESC;


-- QUERY: top_hosts_by_listing_count
SELECT
    hosts.host_id,
    hosts.host_name,
    hosts.host_segment,
    hosts.host_is_superhost,
    COUNT(*) AS listing_count,
    ROUND(
        MEDIAN(facts.price),
        2
    ) AS median_price,
    ROUND(
        AVG(facts.review_scores_rating),
        2
    ) AS average_rating,
    ROUND(
        AVG(
            facts.estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage
FROM dim_host AS hosts
INNER JOIN dim_listing AS listings
    ON hosts.host_key = listings.host_key
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
GROUP BY
    hosts.host_id,
    hosts.host_name,
    hosts.host_segment,
    hosts.host_is_superhost
ORDER BY listing_count DESC
LIMIT 20;


-- QUERY: host_market_concentration
WITH host_listing_counts AS (
    SELECT
        host_key,
        COUNT(*) AS listing_count
    FROM dim_listing
    WHERE host_key IS NOT NULL
    GROUP BY host_key
),

ranked_hosts AS (
    SELECT
        host_key,
        listing_count,
        ROW_NUMBER() OVER (
            ORDER BY listing_count DESC
        ) AS host_rank,
        COUNT(*) OVER () AS total_hosts,
        SUM(listing_count) OVER ()
            AS total_host_linked_listings
    FROM host_listing_counts
)

SELECT
    MAX(total_hosts) AS total_hosts,
    MAX(
        total_host_linked_listings
    ) AS total_host_linked_listings,
    CAST(
        CEIL(
            MAX(total_hosts) * 0.10
        ) AS BIGINT
    ) AS hosts_in_top_10_percent,
    SUM(
        CASE
            WHEN host_rank <= CEIL(
                total_hosts * 0.10
            )
            THEN listing_count
            ELSE 0
        END
    ) AS listings_controlled_by_top_10_percent,
    ROUND(
        SUM(
            CASE
                WHEN host_rank <= CEIL(
                    total_hosts * 0.10
                )
                THEN listing_count
                ELSE 0
            END
        ) * 100.0
        / MAX(
            total_host_linked_listings
        ),
        2
    ) AS top_10_percent_listing_share
FROM ranked_hosts;


-- QUERY: superhost_comparison
SELECT
    CASE
        WHEN hosts.host_is_superhost = TRUE
            THEN 'Superhost'
        WHEN hosts.host_is_superhost = FALSE
            THEN 'Non-Superhost'
        ELSE 'Unknown'
    END AS superhost_status,
    COUNT(
        DISTINCT hosts.host_key
    ) AS host_count,
    COUNT(*) AS listing_count,
    ROUND(
        MEDIAN(facts.price),
        2
    ) AS median_price,
    ROUND(
        AVG(facts.price),
        2
    ) AS average_price,
    ROUND(
        AVG(facts.review_scores_rating),
        2
    ) AS average_rating,
    ROUND(
        AVG(
            facts.estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage,
    ROUND(
        AVG(facts.detailed_review_count),
        2
    ) AS average_detailed_review_count
FROM dim_host AS hosts
INNER JOIN dim_listing AS listings
    ON hosts.host_key = listings.host_key
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
GROUP BY
    CASE
        WHEN hosts.host_is_superhost = TRUE
            THEN 'Superhost'
        WHEN hosts.host_is_superhost = FALSE
            THEN 'Non-Superhost'
        ELSE 'Unknown'
    END
ORDER BY listing_count DESC;


-- QUERY: price_by_review_volume
WITH review_groups AS (
    SELECT
        facts.*,
        CASE
            WHEN facts.detailed_review_count = 0
                THEN 'No Reviews'
            WHEN facts.detailed_review_count
                BETWEEN 1 AND 5
                THEN '1 to 5 Reviews'
            WHEN facts.detailed_review_count
                BETWEEN 6 AND 20
                THEN '6 to 20 Reviews'
            WHEN facts.detailed_review_count
                BETWEEN 21 AND 50
                THEN '21 to 50 Reviews'
            ELSE 'More than 50 Reviews'
        END AS review_volume_group,

        CASE
            WHEN facts.detailed_review_count = 0
                THEN 1
            WHEN facts.detailed_review_count
                BETWEEN 1 AND 5
                THEN 2
            WHEN facts.detailed_review_count
                BETWEEN 6 AND 20
                THEN 3
            WHEN facts.detailed_review_count
                BETWEEN 21 AND 50
                THEN 4
            ELSE 5
        END AS review_group_order
    FROM fact_listing_snapshot AS facts
)

SELECT
    review_volume_group,
    COUNT(*) AS listing_count,
    ROUND(
        MEDIAN(price),
        2
    ) AS median_price,
    ROUND(
        AVG(price),
        2
    ) AS average_price,
    ROUND(
        AVG(review_scores_rating),
        2
    ) AS average_rating,
    ROUND(
        AVG(
            estimated_occupancy_proxy
        ) * 100,
        2
    ) AS average_occupancy_proxy_percentage
FROM review_groups
GROUP BY
    review_volume_group,
    review_group_order
ORDER BY review_group_order;


-- QUERY: monthly_review_activity
SELECT
    dates.year_number,
    dates.month_number,
    dates.month_name,
    COUNT(*) AS review_count,
    COUNT(
        DISTINCT reviews.listing_key
    ) AS listings_reviewed,
    COUNT(
        DISTINCT reviews.reviewer_id
    ) AS unique_reviewers,
    ROUND(
        AVG(reviews.review_length),
        2
    ) AS average_review_length
FROM fact_reviews AS reviews
INNER JOIN dim_date AS dates
    ON reviews.date_key = dates.date_key
GROUP BY
    dates.year_number,
    dates.month_number,
    dates.month_name
ORDER BY
    dates.year_number,
    dates.month_number;


-- QUERY: monthly_availability
SELECT
    dates.year_number,
    dates.month_number,
    dates.month_name,
    COUNT(*) AS calendar_observations,
    SUM(
        CASE
            WHEN calendar.available = TRUE
                THEN 1
            ELSE 0
        END
    ) AS available_days,
    SUM(
        CASE
            WHEN calendar.available = FALSE
                THEN 1
            ELSE 0
        END
    ) AS unavailable_days,
    ROUND(
        AVG(
            CASE
                WHEN calendar.available = TRUE
                    THEN 1.0
                WHEN calendar.available = FALSE
                    THEN 0.0
                ELSE NULL
            END
        ) * 100,
        2
    ) AS availability_rate_percentage,
    ROUND(
        (
            1 - AVG(
                CASE
                    WHEN calendar.available = TRUE
                        THEN 1.0
                    WHEN calendar.available = FALSE
                        THEN 0.0
                    ELSE NULL
                END
            )
        ) * 100,
        2
    ) AS occupancy_proxy_percentage
FROM fact_calendar AS calendar
INNER JOIN dim_date AS dates
    ON calendar.date_key = dates.date_key
GROUP BY
    dates.year_number,
    dates.month_number,
    dates.month_name
ORDER BY
    dates.year_number,
    dates.month_number;


-- QUERY: minimum_nights_by_room_type
SELECT
    listings.room_type,
    COUNT(*) AS listing_count,
    ROUND(
        MEDIAN(facts.minimum_nights),
        2
    ) AS median_minimum_nights,
    ROUND(
        AVG(facts.minimum_nights),
        2
    ) AS average_minimum_nights,
    MIN(
        facts.minimum_nights
    ) AS lowest_minimum_nights,
    MAX(
        facts.minimum_nights
    ) AS highest_minimum_nights
FROM dim_listing AS listings
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
GROUP BY listings.room_type
ORDER BY listing_count DESC;


-- QUERY: listing_source_coverage
SELECT
    listings.record_source,
    listings.has_detailed_record,
    COUNT(*) AS listing_count,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS listing_share_percentage,
    COUNT(facts.price) AS listings_with_price,
    COUNT(
        facts.review_scores_rating
    ) AS listings_with_rating,
    COUNT(
        facts.estimated_occupancy_proxy
    ) AS listings_with_occupancy_proxy
FROM dim_listing AS listings
INNER JOIN fact_listing_snapshot AS facts
    ON listings.listing_key = facts.listing_key
GROUP BY
    listings.record_source,
    listings.has_detailed_record
ORDER BY listing_count DESC;