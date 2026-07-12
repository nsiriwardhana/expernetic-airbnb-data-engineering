from __future__ import annotations

import numpy as np
import pandas as pd


def apply_validation_rules(
    dataframe: pd.DataFrame,
    dataset_name: str,
    rules: dict[str, pd.Series]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply validation rules and return:
    1. The dataset with validation columns
    2. A summary report of failed rules
    """
    validated = dataframe.copy()

    validation_errors = pd.Series(
        "",
        index=validated.index,
        dtype="string"
    )

    report_rows = []

    for rule_name, failure_mask in rules.items():
        failure_mask = (
            failure_mask
            .fillna(False)
            .astype(bool)
        )

        failed_count = int(
            failure_mask.sum()
        )

        failed_percentage = (
            failed_count / len(validated) * 100
            if len(validated) > 0
            else 0
        )

        existing_errors = validation_errors.loc[
            failure_mask
        ]

        validation_errors.loc[
            failure_mask
        ] = np.where(
            existing_errors.eq(""),
            rule_name,
            existing_errors + " | " + rule_name
        )

        report_rows.append({
            "dataset": dataset_name,
            "validation_rule": rule_name,
            "total_rows": len(validated),
            "failed_rows": failed_count,
            "failed_percentage": round(
                failed_percentage,
                4
            ),
            "passed": failed_count == 0
        })

    validated["validation_status"] = np.where(
        validation_errors.eq(""),
        "valid",
        "invalid"
    )

    validated["validation_errors"] = (
        validation_errors.replace(
            "",
            pd.NA
        )
    )

    report = pd.DataFrame(
        report_rows
    )

    return validated, report


def validate_listing_master(
    dataframe: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate the combined listing master dataset.
    """
    rules = {
        "missing_listing_id": (
            dataframe["id"].isna()
        ),

        "duplicate_listing_id": (
            dataframe["id"].duplicated(
                keep=False
            )
        ),

        "negative_price": (
            dataframe["price"].notna()
            & (dataframe["price"] < 0)
        ),

        "invalid_latitude": (
            dataframe["latitude"].notna()
            & ~dataframe["latitude"].between(
                -90,
                90
            )
        ),

        "invalid_longitude": (
            dataframe["longitude"].notna()
            & ~dataframe["longitude"].between(
                -180,
                180
            )
        ),

        "negative_minimum_nights": (
            dataframe["minimum_nights"].notna()
            & (
                dataframe[
                    "minimum_nights"
                ] < 0
            )
        ),

        "negative_review_count": (
            dataframe["number_of_reviews"].notna()
            & (
                dataframe[
                    "number_of_reviews"
                ] < 0
            )
        ),

        "invalid_availability_365": (
            dataframe["availability_365"].notna()
            & ~dataframe[
                "availability_365"
            ].between(
                0,
                365
            )
        )
    }

    return apply_validation_rules(
        dataframe,
        "listing_master",
        rules
    )


def validate_calendar(
    dataframe: pd.DataFrame,
    valid_listing_ids: set[int]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate calendar records.

    The available columns may differ between Inside Airbnb
    city datasets, so optional rules are added only when
    the relevant column exists.
    """
    rules = {}

    if "listing_id" in dataframe.columns:
        rules["missing_listing_id"] = (
            dataframe["listing_id"].isna()
        )

        rules["orphan_listing_id"] = (
            dataframe["listing_id"].notna()
            & ~dataframe["listing_id"].isin(
                valid_listing_ids
            )
        )

    if "date" in dataframe.columns:
        rules["missing_calendar_date"] = (
            dataframe["date"].isna()
        )

    if {
        "listing_id",
        "date"
    }.issubset(dataframe.columns):
        rules["duplicate_listing_date"] = (
            dataframe.duplicated(
                subset=[
                    "listing_id",
                    "date"
                ],
                keep=False
            )
        )

    if "available" in dataframe.columns:
        rules["missing_availability_status"] = (
            dataframe["available"].isna()
        )

    if "price" in dataframe.columns:
        rules["negative_calendar_price"] = (
            dataframe["price"].notna()
            & (
                dataframe["price"] < 0
            )
        )

    if "adjusted_price" in dataframe.columns:
        rules["negative_adjusted_price"] = (
            dataframe["adjusted_price"].notna()
            & (
                dataframe["adjusted_price"] < 0
            )
        )

    if "minimum_nights" in dataframe.columns:
        rules["negative_minimum_nights"] = (
            dataframe[
                "minimum_nights"
            ].notna()
            & (
                dataframe[
                    "minimum_nights"
                ] < 0
            )
        )

    if "maximum_nights" in dataframe.columns:
        rules["negative_maximum_nights"] = (
            dataframe[
                "maximum_nights"
            ].notna()
            & (
                dataframe[
                    "maximum_nights"
                ] < 0
            )
        )

    return apply_validation_rules(
        dataframe,
        "calendar",
        rules
    )


def validate_reviews(
    dataframe: pd.DataFrame,
    valid_listing_ids: set[int]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate detailed review records.
    """
    orphan_listing_mask = (
        dataframe["listing_id"].notna()
        & ~dataframe["listing_id"].isin(
            valid_listing_ids
        )
    )

    rules = {
        "missing_review_id": (
            dataframe["id"].isna()
        ),

        "duplicate_review_id": (
            dataframe["id"].duplicated(
                keep=False
            )
        ),

        "missing_listing_id": (
            dataframe["listing_id"].isna()
        ),

        "orphan_listing_id": (
            orphan_listing_mask
        ),

        "missing_review_date": (
            dataframe["date"].isna()
        )
    }

    return apply_validation_rules(
        dataframe,
        "reviews_detailed",
        rules
    )


def validate_neighbourhoods(
    dataframe: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate neighbourhood reference records.
    """
    neighbourhood_column = (
        "neighbourhood"
        if "neighbourhood" in dataframe.columns
        else dataframe.columns[-1]
    )

    rules = {
        "missing_neighbourhood": (
            dataframe[
                neighbourhood_column
            ].isna()
        ),

        "duplicate_neighbourhood_record": (
            dataframe.duplicated(
                keep=False
            )
        )
    }

    return apply_validation_rules(
        dataframe,
        "neighbourhoods",
        rules
    )