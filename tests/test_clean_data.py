import pandas as pd

from src.clean_data import (
    build_listing_master,
    clean_boolean,
    clean_percentage,
    clean_price
)


def test_clean_price() -> None:
    values = pd.Series([
        "$1,200.50",
        "$85",
        "100.25",
        None,
        ""
    ])

    result = clean_price(values)

    assert result.iloc[0] == 1200.50
    assert result.iloc[1] == 85.00
    assert result.iloc[2] == 100.25
    assert pd.isna(result.iloc[3])
    assert pd.isna(result.iloc[4])


def test_clean_percentage() -> None:
    values = pd.Series([
        "98%",
        "75%",
        "0.50",
        None
    ])

    result = clean_percentage(values)

    assert result.iloc[0] == 0.98
    assert result.iloc[1] == 0.75
    assert result.iloc[2] == 0.50
    assert pd.isna(result.iloc[3])


def test_clean_boolean() -> None:
    values = pd.Series([
        "t",
        "f",
        "True",
        "False",
        "yes",
        "no",
        None
    ])

    result = clean_boolean(values)

    assert result.iloc[0] == True
    assert result.iloc[1] == False
    assert result.iloc[2] == True
    assert result.iloc[3] == False
    assert result.iloc[4] == True
    assert result.iloc[5] == False
    assert pd.isna(result.iloc[6])


def test_build_listing_master() -> None:
    detailed = pd.DataFrame({
        "id": pd.Series(
            [1, 2],
            dtype="Int64"
        ),
        "name": [
            "Listing One",
            "Listing Two"
        ],
        "neighbourhood_cleansed": [
            "Area A",
            "Area B"
        ]
    })

    summary = pd.DataFrame({
        "id": pd.Series(
            [1, 2, 3],
            dtype="Int64"
        ),
        "name": [
            "Listing One",
            "Listing Two",
            "Listing Three"
        ],
        "neighbourhood": [
            "Area A",
            "Area B",
            "Area C"
        ]
    })

    result = build_listing_master(
        detailed,
        summary
    )

    assert len(result) == 3
    assert result["id"].nunique() == 3
    assert result["id"].duplicated().sum() == 0

    source_counts = (
        result["record_source"]
        .value_counts()
        .to_dict()
    )

    assert source_counts["detailed"] == 2
    assert source_counts["summary_only"] == 1

    summary_only_record = result.loc[
        result["id"] == 3
    ].iloc[0]

    assert (
        summary_only_record[
            "neighbourhood_cleansed"
        ]
        == "Area C"
    )