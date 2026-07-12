from pathlib import Path

import pandas as pd

from src.validate_data import (
    validate_calendar,
    validate_listing_master,
    validate_neighbourhoods,
    validate_reviews
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

PROCESSED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

VALIDATED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validated"
)

QUARANTINE_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "quarantine"
)

QUALITY_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "data_quality"
)


def save_validation_results(
    validated_dataframe: pd.DataFrame,
    dataset_name: str
) -> None:
    """
    Save valid and invalid records separately.
    """
    valid_records = validated_dataframe[
        validated_dataframe[
            "validation_status"
        ] == "valid"
    ].copy()

    invalid_records = validated_dataframe[
        validated_dataframe[
            "validation_status"
        ] == "invalid"
    ].copy()

    valid_records.to_parquet(
        VALIDATED_DIRECTORY
        / f"{dataset_name}_valid.parquet",
        index=False
    )

    invalid_records.to_parquet(
        QUARANTINE_DIRECTORY
        / f"{dataset_name}_invalid.parquet",
        index=False
    )

    print(
        f"{dataset_name}: "
        f"{len(valid_records):,} valid, "
        f"{len(invalid_records):,} invalid"
    )


def main() -> None:
    print("Starting validation process")

    VALIDATED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    QUARANTINE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    QUALITY_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Loading processed datasets")

    listing_master = pd.read_parquet(
        PROCESSED_DIRECTORY
        / "listing_master.parquet"
    )

    calendar = pd.read_parquet(
        PROCESSED_DIRECTORY
        / "calendar_clean.parquet"
    )

    reviews = pd.read_parquet(
        PROCESSED_DIRECTORY
        / "reviews_detailed_clean.parquet"
    )

    neighbourhoods = pd.read_parquet(
        PROCESSED_DIRECTORY
        / "neighbourhoods_clean.parquet"
    )

    valid_listing_ids = set(
        listing_master["id"]
        .dropna()
        .astype("int64")
    )

    listing_completeness_report = pd.DataFrame([
    {
        "dataset": "listing_master",
        "quality_issue": "missing_price",
        "affected_rows": int(
            listing_master["price"].isna().sum()
        ),
        "affected_percentage": round(
            listing_master["price"].isna().mean() * 100,
            4
        ),
        "severity": "warning",
        "action": (
            "Retained as an explicit null and excluded "
            "only from price-specific analysis"
        )
    }
    ])

    listing_completeness_report.to_csv(
        QUALITY_OUTPUT_DIRECTORY
        / "listing_completeness_report.csv",
        index=False
    )

    print("Validating listing master")

    (
        listing_master_validated,
        listing_report
    ) = validate_listing_master(
        listing_master
    )

    print("Validating calendar")

    (
        calendar_validated,
        calendar_report
    ) = validate_calendar(
        calendar,
        valid_listing_ids
    )

    print("Validating reviews")

    (
        reviews_validated,
        reviews_report
    ) = validate_reviews(
        reviews,
        valid_listing_ids
    )

    print("Validating neighbourhoods")

    (
        neighbourhoods_validated,
        neighbourhoods_report
    ) = validate_neighbourhoods(
        neighbourhoods
    )

    print("\nSaving valid and quarantined records")

    save_validation_results(
        listing_master_validated,
        "listing_master"
    )

    save_validation_results(
        calendar_validated,
        "calendar"
    )

    save_validation_results(
        reviews_validated,
        "reviews_detailed"
    )

    save_validation_results(
        neighbourhoods_validated,
        "neighbourhoods"
    )

    validation_report = pd.concat(
        [
            listing_report,
            calendar_report,
            reviews_report,
            neighbourhoods_report
        ],
        ignore_index=True
    )

    validation_report.to_csv(
        QUALITY_OUTPUT_DIRECTORY
        / "validation_report.csv",
        index=False
    )

    failed_rules = validation_report[
        validation_report[
            "failed_rows"
        ] > 0
    ].copy()

    failed_rules.to_csv(
        QUALITY_OUTPUT_DIRECTORY
        / "failed_validation_rules.csv",
        index=False
    )

    print("\nValidation report")

    print(
        validation_report[
            [
                "dataset",
                "validation_rule",
                "failed_rows",
                "failed_percentage"
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nValidation completed successfully"
    )

    print(
        "Report saved to:",
        QUALITY_OUTPUT_DIRECTORY
        / "validation_report.csv"
    )


if __name__ == "__main__":
    main()