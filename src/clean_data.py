from __future__ import annotations

import pandas as pd


def clean_price(series: pd.Series) -> pd.Series:
    """
    Convert price values such as '$1,250.00' into numeric values.
    Works with both text and already numeric columns.
    """
    cleaned = (
        series.astype("string")
        .str.replace(r"[^\d.\-]", "", regex=True)
        .str.strip()
        .replace("", pd.NA)
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    ).astype("Float64")


def clean_percentage(series: pd.Series) -> pd.Series:
    """
    Convert percentage values such as '98%' into 0.98.
    """
    text_values = (
        series.astype("string")
        .str.strip()
    )

    contains_percentage_symbol = (
        text_values.str.contains(
            "%",
            regex=False,
            na=False
        )
    )

    cleaned = (
        text_values
        .str.replace("%", "", regex=False)
        .replace("", pd.NA)
    )

    numeric_values = pd.to_numeric(
        cleaned,
        errors="coerce"
    ).astype("Float64")

    numeric_values.loc[
        contains_percentage_symbol
    ] = (
        numeric_values.loc[
            contains_percentage_symbol
        ] / 100
    )

    numeric_values.loc[
        ~contains_percentage_symbol
        & (numeric_values > 1)
    ] = (
        numeric_values.loc[
            ~contains_percentage_symbol
            & (numeric_values > 1)
        ] / 100
    )

    return numeric_values


def clean_boolean(series: pd.Series) -> pd.Series:
    """
    Convert values such as t/f, true/false, and yes/no into Boolean values.
    """
    mapping = {
        "t": True,
        "true": True,
        "1": True,
        "yes": True,
        "y": True,
        "f": False,
        "false": False,
        "0": False,
        "no": False,
        "n": False
    }

    cleaned = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map(mapping)
    )

    return cleaned.astype("boolean")


def clean_text(series: pd.Series) -> pd.Series:
    """
    Remove leading and trailing spaces from text columns.
    Empty strings are converted to missing values.
    """
    return (
        series.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


def clean_listings(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean either the detailed or summary listings dataset.
    """
    cleaned = dataframe.copy()

    price_columns = [
        "price"
    ]

    percentage_columns = [
        "host_response_rate",
        "host_acceptance_rate"
    ]

    date_columns = [
        "last_scraped",
        "host_since",
        "calendar_last_scraped",
        "first_review",
        "last_review"
    ]

    boolean_columns = [
        "host_is_superhost",
        "host_has_profile_pic",
        "host_identity_verified",
        "has_availability",
        "instant_bookable"
    ]

    identifier_columns = [
        "id",
        "host_id",
        "scrape_id"
    ]

    integer_columns = [
        "accommodates",
        "minimum_nights",
        "maximum_nights",
        "number_of_reviews",
        "number_of_reviews_ltm",
        "number_of_reviews_l30d",
        "calculated_host_listings_count",
        "availability_30",
        "availability_60",
        "availability_90",
        "availability_365"
    ]

    float_columns = [
        "latitude",
        "longitude",
        "bathrooms",
        "bedrooms",
        "beds",
        "reviews_per_month",
        "review_scores_rating",
        "review_scores_accuracy",
        "review_scores_cleanliness",
        "review_scores_checkin",
        "review_scores_communication",
        "review_scores_location",
        "review_scores_value"
    ]

    text_columns = [
        "name",
        "host_name",
        "neighbourhood",
        "neighbourhood_cleansed",
        "neighbourhood_group_cleansed",
        "property_type",
        "room_type",
        "bathrooms_text",
        "license"
    ]

    for column in price_columns:
        if column in cleaned.columns:
            cleaned[column] = clean_price(
                cleaned[column]
            )

    for column in percentage_columns:
        if column in cleaned.columns:
            cleaned[column] = clean_percentage(
                cleaned[column]
            )

    for column in date_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(
                cleaned[column],
                errors="coerce"
            )

    for column in boolean_columns:
        if column in cleaned.columns:
            cleaned[column] = clean_boolean(
                cleaned[column]
            )

    for column in identifier_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(
                cleaned[column],
                errors="coerce"
            ).astype("Int64")

    for column in integer_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(
                cleaned[column],
                errors="coerce"
            ).astype("Int64")

    for column in float_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(
                cleaned[column],
                errors="coerce"
            ).astype("Float64")

    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = clean_text(
                cleaned[column]
            )

    return cleaned


def build_listing_master(
    detailed_listings: pd.DataFrame,
    summary_listings: pd.DataFrame
) -> pd.DataFrame:
    """
    Build a complete listing master table.

    Detailed records are used when available.
    Listings available only in the summary file are appended.
    """
    detailed = detailed_listings.copy()
    summary = summary_listings.copy()

    detailed_ids = set(
        detailed["id"]
        .dropna()
        .astype("int64")
    )

    summary_only = summary[
        ~summary["id"].isin(detailed_ids)
    ].copy()

    if "neighbourhood" in summary_only.columns:
        summary_only[
            "neighbourhood_cleansed"
        ] = summary_only["neighbourhood"]

    detailed["record_source"] = "detailed"
    detailed["has_detailed_record"] = True

    summary_only["record_source"] = "summary_only"
    summary_only["has_detailed_record"] = False

    all_columns = list(
        dict.fromkeys(
            list(detailed.columns)
            + list(summary_only.columns)
        )
    )

    detailed = detailed.reindex(
        columns=all_columns
    )

    summary_only = summary_only.reindex(
        columns=all_columns
    )

    listing_master = pd.concat(
        [
            detailed,
            summary_only
        ],
        ignore_index=True
    )

    listing_master = (
        listing_master
        .sort_values("id")
        .drop_duplicates(
            subset=["id"],
            keep="first"
        )
        .reset_index(drop=True)
    )

    return listing_master


def clean_calendar(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean the calendar dataset.
    """
    cleaned = dataframe.copy()

    if "listing_id" in cleaned.columns:
        cleaned["listing_id"] = pd.to_numeric(
            cleaned["listing_id"],
            errors="coerce"
        ).astype("Int64")

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(
            cleaned["date"],
            errors="coerce"
        )

    for column in [
        "price",
        "adjusted_price"
    ]:
        if column in cleaned.columns:
            cleaned[column] = clean_price(
                cleaned[column]
            )

    if "available" in cleaned.columns:
        cleaned["available"] = clean_boolean(
            cleaned["available"]
        )

    for column in [
        "minimum_nights",
        "maximum_nights"
    ]:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(
                cleaned[column],
                errors="coerce"
            ).astype("Int64")

    return cleaned


def clean_reviews(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean either the detailed or summary reviews dataset.
    """
    cleaned = dataframe.copy()

    identifier_columns = [
        "id",
        "listing_id",
        "reviewer_id"
    ]

    for column in identifier_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(
                cleaned[column],
                errors="coerce"
            ).astype("Int64")

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(
            cleaned["date"],
            errors="coerce"
        )

    for column in [
        "reviewer_name",
        "comments"
    ]:
        if column in cleaned.columns:
            cleaned[column] = clean_text(
                cleaned[column]
            )

    if "comments" in cleaned.columns:
        cleaned["review_length"] = (
            cleaned["comments"]
            .fillna("")
            .str.len()
            .astype("Int64")
        )

    return cleaned


def clean_neighbourhoods(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean neighbourhood reference data.
    """
    cleaned = dataframe.copy()

    for column in cleaned.columns:
        if (
            pd.api.types.is_object_dtype(
                cleaned[column]
            )
            or pd.api.types.is_string_dtype(
                cleaned[column]
            )
        ):
            cleaned[column] = clean_text(
                cleaned[column]
            )

    cleaned = (
        cleaned
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return cleaned