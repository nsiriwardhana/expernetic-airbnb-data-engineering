from __future__ import annotations

import numpy as np
import pandas as pd


def build_calendar_summary(
    calendar: pd.DataFrame
) -> pd.DataFrame:
    """
    Create one calendar summary record per listing.

    Unavailable dates are used only as an estimated occupancy
    proxy because unavailability does not confirm a booking.
    """
    summary = (
        calendar
        .groupby(
            "listing_id",
            dropna=False
        )
        .agg(
            calendar_start=("date", "min"),
            calendar_end=("date", "max"),
            calendar_days=("date", "nunique"),
            availability_observations=(
                "available",
                "count"
            ),
            available_days=(
                "available",
                lambda values: int(
                    values.eq(True).sum()
                )
            ),
            unavailable_days=(
                "available",
                lambda values: int(
                    values.eq(False).sum()
                )
            ),
            missing_availability_days=(
                "available",
                lambda values: int(
                    values.isna().sum()
                )
            ),
            median_minimum_nights=(
                "minimum_nights",
                "median"
            ),
            median_maximum_nights=(
                "maximum_nights",
                "median"
            )
        )
        .reset_index()
    )

    summary[
        "estimated_occupancy_proxy"
    ] = np.where(
        summary[
            "availability_observations"
        ] > 0,
        (
            summary["unavailable_days"]
            / summary[
                "availability_observations"
            ]
        ),
        np.nan
    )

    summary[
        "estimated_availability_rate"
    ] = np.where(
        summary[
            "availability_observations"
        ] > 0,
        (
            summary["available_days"]
            / summary[
                "availability_observations"
            ]
        ),
        np.nan
    )

    return summary


def build_review_summary(
    reviews: pd.DataFrame
) -> pd.DataFrame:
    """
    Create one detailed review summary record per listing.
    """
    aggregations = {
        "first_detailed_review_date": (
            "date",
            "min"
        ),
        "last_detailed_review_date": (
            "date",
            "max"
        )
    }

    if "id" in reviews.columns:
        aggregations[
            "detailed_review_count"
        ] = (
            "id",
            "nunique"
        )
    else:
        aggregations[
            "detailed_review_count"
        ] = (
            "listing_id",
            "size"
        )

    if "reviewer_id" in reviews.columns:
        aggregations[
            "unique_reviewer_count"
        ] = (
            "reviewer_id",
            "nunique"
        )

    if "review_length" in reviews.columns:
        aggregations[
            "average_review_length"
        ] = (
            "review_length",
            "mean"
        )

        aggregations[
            "median_review_length"
        ] = (
            "review_length",
            "median"
        )

    summary = (
        reviews
        .groupby(
            "listing_id",
            dropna=False
        )
        .agg(**aggregations)
        .reset_index()
    )

    return summary


def determine_host_portfolio_size(
    listings: pd.DataFrame
) -> pd.Series:
    """
    Select the most suitable available host listing-count field.
    """
    candidate_columns = [
        "calculated_host_listings_count",
        "host_listings_count",
        "host_total_listings_count"
    ]

    for column in candidate_columns:
        if column in listings.columns:
            return pd.to_numeric(
                listings[column],
                errors="coerce"
            )

    return pd.Series(
        pd.NA,
        index=listings.index,
        dtype="Float64"
    )


def create_host_segment(
    portfolio_size: pd.Series
) -> pd.Series:
    """
    Classify hosts according to portfolio size.
    """
    numeric_size = pd.to_numeric(
        portfolio_size,
        errors="coerce"
    )

    result = pd.Series(
        "Unknown",
        index=portfolio_size.index,
        dtype="string"
    )

    result.loc[
        numeric_size.eq(1).fillna(False)
    ] = "Single Listing"

    result.loc[
        numeric_size.between(
            2,
            5,
            inclusive="both"
        ).fillna(False)
    ] = "Small Portfolio"

    result.loc[
        numeric_size.between(
            6,
            20,
            inclusive="both"
        ).fillna(False)
    ] = "Medium Portfolio"

    result.loc[
        numeric_size.gt(20).fillna(False)
    ] = "Large Operator"

    return result


def enrich_listing_master(
    listings: pd.DataFrame,
    calendar_summary: pd.DataFrame,
    review_summary: pd.DataFrame,
    snapshot_date: str = "2026-06-29"
) -> pd.DataFrame:
    """
    Join listings, calendar summaries, and review summaries,
    then create useful analytical fields.
    """
    enriched = listings.copy()

    enriched = enriched.merge(
        calendar_summary,
        how="left",
        left_on="id",
        right_on="listing_id",
        validate="one_to_one"
    )

    if "listing_id" in enriched.columns:
        enriched = enriched.drop(
            columns=["listing_id"]
        )

    enriched = enriched.merge(
        review_summary,
        how="left",
        left_on="id",
        right_on="listing_id",
        validate="one_to_one"
    )

    if "listing_id" in enriched.columns:
        enriched = enriched.drop(
            columns=["listing_id"]
        )

    fixed_snapshot_date = pd.Timestamp(
        snapshot_date
    )

    if "last_scraped" in enriched.columns:
        listing_snapshot_date = (
            pd.to_datetime(
                enriched["last_scraped"],
                errors="coerce"
            )
            .fillna(fixed_snapshot_date)
        )
    else:
        listing_snapshot_date = pd.Series(
            fixed_snapshot_date,
            index=enriched.index
        )

    enriched["analysis_snapshot_date"] = (
        listing_snapshot_date
    )

    if "host_since" in enriched.columns:
        host_since = pd.to_datetime(
            enriched["host_since"],
            errors="coerce"
        )

        tenure_days = (
            listing_snapshot_date -
            host_since
        ).dt.days

        tenure_days = tenure_days.where(
            tenure_days >= 0
        )

        enriched["host_tenure_years"] = (
            tenure_days / 365.25
        ).round(2)

    if {
        "price",
        "bedrooms"
    }.issubset(enriched.columns):
        valid_bedrooms = (
            enriched["bedrooms"]
            .where(
                enriched["bedrooms"] > 0
            )
        )

        enriched["price_per_bedroom"] = (
            enriched["price"]
            / valid_bedrooms
        )

    if {
        "price",
        "accommodates"
    }.issubset(enriched.columns):
        valid_capacity = (
            enriched["accommodates"]
            .where(
                enriched[
                    "accommodates"
                ] > 0
            )
        )

        enriched["price_per_guest"] = (
            enriched["price"]
            / valid_capacity
        )

    portfolio_size = (
        determine_host_portfolio_size(
            enriched
        )
    )

    enriched["host_portfolio_size"] = (
        portfolio_size
    )

    enriched["host_segment"] = (
        create_host_segment(
            portfolio_size
        )
    )

    if "room_type" in enriched.columns:
        enriched["is_entire_home"] = (
            enriched["room_type"]
            .eq("Entire home/apt")
            .astype("boolean")
        )

    if "detailed_review_count" in enriched.columns:
        enriched[
            "detailed_review_count"
        ] = (
            enriched[
                "detailed_review_count"
            ]
            .fillna(0)
            .astype("Int64")
        )

        enriched["has_detailed_reviews"] = (
            enriched[
                "detailed_review_count"
            ] > 0
        ).astype("boolean")

    if "calendar_days" in enriched.columns:
        enriched["has_calendar_record"] = (
            enriched[
                "calendar_days"
            ].notna()
        ).astype("boolean")

    if "last_detailed_review_date" in enriched.columns:
        last_review = pd.to_datetime(
            enriched[
                "last_detailed_review_date"
            ],
            errors="coerce"
        )

        days_since_review = (
            listing_snapshot_date -
            last_review
        ).dt.days

        enriched[
            "days_since_last_review"
        ] = days_since_review.where(
            days_since_review >= 0
        )

    if {
        "detailed_review_count",
        "host_tenure_years"
    }.issubset(enriched.columns):
        valid_tenure = enriched[
            "host_tenure_years"
        ].where(
            enriched[
                "host_tenure_years"
            ] > 0
        )

        enriched[
            "reviews_per_host_year"
        ] = (
            enriched[
                "detailed_review_count"
            ]
            / valid_tenure
        )

    return enriched


def build_neighbourhood_summary(
    listings: pd.DataFrame
) -> pd.DataFrame:
    """
    Create neighbourhood-level market aggregates.
    """
    neighbourhood_column = (
        "neighbourhood_cleansed"
    )

    if neighbourhood_column not in listings.columns:
        raise KeyError(
            "neighbourhood_cleansed is missing "
            "from the enriched listings dataset."
        )

    grouped = listings.groupby(
        neighbourhood_column,
        dropna=False
    )

    summary = grouped["id"].nunique().rename(
        "listing_count"
    ).to_frame()

    if "host_id" in listings.columns:
        summary["unique_host_count"] = (
            grouped["host_id"].nunique()
        )

    if "price" in listings.columns:
        summary["median_price"] = (
            grouped["price"].median()
        )

        summary["average_price"] = (
            grouped["price"].mean()
        )

    if "review_scores_rating" in listings.columns:
        summary["average_review_rating"] = (
            grouped[
                "review_scores_rating"
            ].mean()
        )

    if (
        "estimated_occupancy_proxy"
        in listings.columns
    ):
        summary[
            "average_occupancy_proxy"
        ] = (
            grouped[
                "estimated_occupancy_proxy"
            ].mean()
        )

    if "minimum_nights" in listings.columns:
        summary["median_minimum_nights"] = (
            grouped[
                "minimum_nights"
            ].median()
        )

    if "room_type" in listings.columns:
        summary[
            "entire_home_share_percentage"
        ] = grouped["room_type"].apply(
            lambda values: round(
                values.eq(
                    "Entire home/apt"
                ).mean() * 100,
                2
            )
        )

    if "record_source" in listings.columns:
        summary[
            "detailed_record_share_percentage"
        ] = grouped[
            "record_source"
        ].apply(
            lambda values: round(
                values.eq(
                    "detailed"
                ).mean() * 100,
                2
            )
        )

    summary = (
        summary
        .reset_index()
        .sort_values(
            "listing_count",
            ascending=False
        )
        .reset_index(drop=True)
    )

    numeric_columns = (
        summary.select_dtypes(
            include="number"
        ).columns
    )

    summary[numeric_columns] = (
        summary[numeric_columns]
        .round(4)
    )

    return summary