import pandas as pd
import pytest

from src.enrich_data import (
    build_calendar_summary,
    build_review_summary,
    create_host_segment
)


def test_create_host_segment() -> None:
    portfolio_sizes = pd.Series([
        1,
        3,
        10,
        25,
        pd.NA
    ])

    result = create_host_segment(
        portfolio_sizes
    )

    assert result.iloc[0] == "Single Listing"
    assert result.iloc[1] == "Small Portfolio"
    assert result.iloc[2] == "Medium Portfolio"
    assert result.iloc[3] == "Large Operator"
    assert result.iloc[4] == "Unknown"


def test_calendar_summary() -> None:
    calendar = pd.DataFrame({
        "listing_id": pd.Series(
            [1, 1, 1, 2, 2],
            dtype="Int64"
        ),
        "date": pd.to_datetime([
            "2026-07-01",
            "2026-07-02",
            "2026-07-03",
            "2026-07-01",
            "2026-07-02"
        ]),
        "available": pd.Series(
            [
                True,
                False,
                False,
                True,
                True
            ],
            dtype="boolean"
        ),
        "minimum_nights": pd.Series(
            [1, 1, 1, 2, 2],
            dtype="Int64"
        ),
        "maximum_nights": pd.Series(
            [365, 365, 365, 30, 30],
            dtype="Int64"
        )
    })

    result = build_calendar_summary(
        calendar
    )

    listing_one = result.loc[
        result["listing_id"] == 1
    ].iloc[0]

    assert listing_one["calendar_days"] == 3
    assert listing_one["available_days"] == 1
    assert listing_one["unavailable_days"] == 2

    assert (
        listing_one[
            "estimated_occupancy_proxy"
        ]
        == pytest.approx(
            2 / 3
        )
    )


def test_review_summary() -> None:
    reviews = pd.DataFrame({
        "id": pd.Series(
            [10, 11, 12],
            dtype="Int64"
        ),
        "listing_id": pd.Series(
            [1, 1, 2],
            dtype="Int64"
        ),
        "reviewer_id": pd.Series(
            [100, 101, 102],
            dtype="Int64"
        ),
        "date": pd.to_datetime([
            "2026-01-01",
            "2026-02-01",
            "2026-03-01"
        ]),
        "review_length": pd.Series(
            [20, 40, 30],
            dtype="Int64"
        )
    })

    result = build_review_summary(
        reviews
    )

    listing_one = result.loc[
        result["listing_id"] == 1
    ].iloc[0]

    assert (
        listing_one[
            "detailed_review_count"
        ]
        == 2
    )

    assert (
        listing_one[
            "unique_reviewer_count"
        ]
        == 2
    )

    assert (
        listing_one[
            "average_review_length"
        ]
        == 30
    )