import pandas as pd

from src.validate_data import (
    validate_calendar,
    validate_listing_master,
    validate_reviews
)


def create_valid_listing_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "id": pd.Series(
            [1, 2],
            dtype="Int64"
        ),
        "price": pd.Series(
            [100.0, pd.NA],
            dtype="Float64"
        ),
        "latitude": pd.Series(
            [1.30, 1.31],
            dtype="Float64"
        ),
        "longitude": pd.Series(
            [103.80, 103.81],
            dtype="Float64"
        ),
        "minimum_nights": pd.Series(
            [1, 2],
            dtype="Int64"
        ),
        "number_of_reviews": pd.Series(
            [10, 0],
            dtype="Int64"
        ),
        "availability_365": pd.Series(
            [100, 365],
            dtype="Int64"
        )
    })


def test_missing_price_is_warning_not_failure() -> None:
    listings = create_valid_listing_dataframe()

    validated, report = validate_listing_master(
        listings
    )

    assert (
        validated["validation_status"]
        == "valid"
    ).all()

    assert "missing_price" not in (
        report["validation_rule"].tolist()
    )


def test_negative_price_is_invalid() -> None:
    listings = create_valid_listing_dataframe()

    listings.loc[
        listings["id"] == 1,
        "price"
    ] = -10

    validated, report = validate_listing_master(
        listings
    )

    failed_record = validated.loc[
        validated["id"] == 1
    ].iloc[0]

    assert (
        failed_record["validation_status"]
        == "invalid"
    )

    assert "negative_price" in str(
        failed_record["validation_errors"]
    )

    negative_price_report = report.loc[
        report["validation_rule"]
        == "negative_price"
    ].iloc[0]

    assert negative_price_report["failed_rows"] == 1


def test_duplicate_calendar_key_is_invalid() -> None:
    calendar = pd.DataFrame({
        "listing_id": pd.Series(
            [1, 1],
            dtype="Int64"
        ),
        "date": pd.to_datetime([
            "2026-07-01",
            "2026-07-01"
        ]),
        "available": pd.Series(
            [True, False],
            dtype="boolean"
        ),
        "minimum_nights": pd.Series(
            [1, 1],
            dtype="Int64"
        ),
        "maximum_nights": pd.Series(
            [365, 365],
            dtype="Int64"
        )
    })

    validated, report = validate_calendar(
        calendar,
        valid_listing_ids={1}
    )

    assert (
        validated["validation_status"]
        == "invalid"
    ).all()

    duplicate_report = report.loc[
        report["validation_rule"]
        == "duplicate_listing_date"
    ].iloc[0]

    assert duplicate_report["failed_rows"] == 2


def test_orphan_review_is_invalid() -> None:
    reviews = pd.DataFrame({
        "id": pd.Series(
            [100],
            dtype="Int64"
        ),
        "listing_id": pd.Series(
            [999],
            dtype="Int64"
        ),
        "reviewer_id": pd.Series(
            [50],
            dtype="Int64"
        ),
        "date": pd.to_datetime([
            "2026-01-10"
        ])
    })

    validated, report = validate_reviews(
        reviews,
        valid_listing_ids={1, 2}
    )

    assert (
        validated.iloc[0][
            "validation_status"
        ]
        == "invalid"
    )

    assert "orphan_listing_id" in str(
        validated.iloc[0][
            "validation_errors"
        ]
    )

    orphan_report = report.loc[
        report["validation_rule"]
        == "orphan_listing_id"
    ].iloc[0]

    assert orphan_report["failed_rows"] == 1