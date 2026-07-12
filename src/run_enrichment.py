from pathlib import Path

import pandas as pd

from src.enrich_data import (
    build_calendar_summary,
    build_neighbourhood_summary,
    build_review_summary,
    enrich_listing_master
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

VALIDATED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validated"
)

ENRICHED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "enriched"
)

QUALITY_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "data_quality"
)


def main() -> None:
    print("Starting enrichment process")

    ENRICHED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    QUALITY_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Loading validated datasets")

    listings = pd.read_parquet(
        VALIDATED_DIRECTORY
        / "listing_master_valid.parquet"
    )

    calendar = pd.read_parquet(
        VALIDATED_DIRECTORY
        / "calendar_valid.parquet"
    )

    reviews = pd.read_parquet(
        VALIDATED_DIRECTORY
        / "reviews_detailed_valid.parquet"
    )

    print("Creating calendar summary")

    calendar_summary = (
        build_calendar_summary(
            calendar
        )
    )

    print("Creating review summary")

    review_summary = (
        build_review_summary(
            reviews
        )
    )

    print("Creating enriched listing master")

    listing_enriched = (
        enrich_listing_master(
            listings=listings,
            calendar_summary=calendar_summary,
            review_summary=review_summary,
            snapshot_date="2026-06-29"
        )
    )

    print("Creating neighbourhood summary")

    neighbourhood_summary = (
        build_neighbourhood_summary(
            listing_enriched
        )
    )

    print("Saving enriched datasets")

    calendar_summary.to_parquet(
        ENRICHED_DIRECTORY
        / "calendar_listing_summary.parquet",
        index=False
    )

    review_summary.to_parquet(
        ENRICHED_DIRECTORY
        / "review_listing_summary.parquet",
        index=False
    )

    listing_enriched.to_parquet(
        ENRICHED_DIRECTORY
        / "listing_enriched.parquet",
        index=False
    )

    neighbourhood_summary.to_parquet(
        ENRICHED_DIRECTORY
        / "neighbourhood_summary.parquet",
        index=False
    )

    listings_with_calendar = int(
        listing_enriched[
            "calendar_days"
        ].notna().sum()
    )

    listings_with_reviews = int(
        (
            listing_enriched[
                "detailed_review_count"
            ] > 0
        ).sum()
    )

    coverage_report = pd.DataFrame([
        {
            "metric": "Validated listings",
            "value": len(listings)
        },
        {
            "metric": "Calendar summary rows",
            "value": len(calendar_summary)
        },
        {
            "metric": "Review summary rows",
            "value": len(review_summary)
        },
        {
            "metric": "Listings with calendar records",
            "value": listings_with_calendar
        },
        {
            "metric": "Listings with detailed reviews",
            "value": listings_with_reviews
        },
        {
            "metric": "Neighbourhood summary rows",
            "value": len(
                neighbourhood_summary
            )
        }
    ])

    coverage_report.to_csv(
        QUALITY_OUTPUT_DIRECTORY
        / "enrichment_coverage_report.csv",
        index=False
    )

    print("\nEnrichment completed successfully")

    print(
        "Listing enriched:",
        listing_enriched.shape
    )

    print(
        "Calendar summary:",
        calendar_summary.shape
    )

    print(
        "Review summary:",
        review_summary.shape
    )

    print(
        "Neighbourhood summary:",
        neighbourhood_summary.shape
    )

    print(
        "\nListings with calendar records:",
        f"{listings_with_calendar:,}"
    )

    print(
        "Listings with detailed reviews:",
        f"{listings_with_reviews:,}"
    )

    print(
        "\nHost segments:"
    )

    print(
        listing_enriched[
            "host_segment"
        ].value_counts(
            dropna=False
        )
    )


if __name__ == "__main__":
    main()