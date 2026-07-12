from pathlib import Path

import pandas as pd

from src.clean_data import (
    build_listing_master,
    clean_calendar,
    clean_listings,
    clean_neighbourhoods,
    clean_reviews
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

RAW_DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "singapore"
)

PROCESSED_DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


def main() -> None:
    print("Starting data cleaning process")

    PROCESSED_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Loading raw datasets")

    listings_detailed_raw = pd.read_csv(
        RAW_DATA_DIRECTORY
        / "listings.csv.gz",
        low_memory=False
    )

    listings_summary_raw = pd.read_csv(
        RAW_DATA_DIRECTORY
        / "listings.csv",
        low_memory=False
    )

    calendar_raw = pd.read_csv(
        RAW_DATA_DIRECTORY
        / "calendar.csv.gz",
        low_memory=False
    )

    reviews_detailed_raw = pd.read_csv(
        RAW_DATA_DIRECTORY
        / "reviews.csv.gz",
        low_memory=False
    )

    reviews_summary_raw = pd.read_csv(
        RAW_DATA_DIRECTORY
        / "reviews.csv",
        low_memory=False
    )

    neighbourhoods_raw = pd.read_csv(
        RAW_DATA_DIRECTORY
        / "neighbourhoods.csv",
        low_memory=False
    )

    print("Cleaning listings")

    listings_detailed_clean = clean_listings(
        listings_detailed_raw
    )

    listings_summary_clean = clean_listings(
        listings_summary_raw
    )

    listing_master = build_listing_master(
        listings_detailed_clean,
        listings_summary_clean
    )

    print("Cleaning calendar")

    calendar_clean = clean_calendar(
        calendar_raw
    )

    print("Cleaning reviews")

    reviews_detailed_clean = clean_reviews(
        reviews_detailed_raw
    )

    reviews_summary_clean = clean_reviews(
        reviews_summary_raw
    )

    print("Cleaning neighbourhoods")

    neighbourhoods_clean = clean_neighbourhoods(
        neighbourhoods_raw
    )

    print("Saving cleaned Parquet files")

    listings_detailed_clean.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "listings_detailed_clean.parquet",
        index=False
    )

    listings_summary_clean.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "listings_summary_clean.parquet",
        index=False
    )

    listing_master.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "listing_master.parquet",
        index=False
    )

    calendar_clean.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "calendar_clean.parquet",
        index=False
    )

    reviews_detailed_clean.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "reviews_detailed_clean.parquet",
        index=False
    )

    reviews_summary_clean.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "reviews_summary_clean.parquet",
        index=False
    )

    neighbourhoods_clean.to_parquet(
        PROCESSED_DATA_DIRECTORY
        / "neighbourhoods_clean.parquet",
        index=False
    )

    print("\nCleaning completed successfully")

    print(
        "Detailed listings:",
        listings_detailed_clean.shape
    )

    print(
        "Summary listings:",
        listings_summary_clean.shape
    )

    print(
        "Listing master:",
        listing_master.shape
    )

    print(
        "Calendar:",
        calendar_clean.shape
    )

    print(
        "Detailed reviews:",
        reviews_detailed_clean.shape
    )

    print(
        "Summary reviews:",
        reviews_summary_clean.shape
    )

    print(
        "Neighbourhoods:",
        neighbourhoods_clean.shape
    )

    print("\nListing master record sources:")

    print(
        listing_master[
            "record_source"
        ].value_counts()
    )


if __name__ == "__main__":
    main()