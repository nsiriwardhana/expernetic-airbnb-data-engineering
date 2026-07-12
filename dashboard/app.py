from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Singapore Airbnb Market Intelligence",
    page_icon="🏠",
    layout="wide"
)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "database"
    / "airbnb_singapore.duckdb"
)

STATISTICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "statistics"
    / "statistical_results.csv"
)

VALIDATION_REPORT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "data_quality"
    / "validation_report.csv"
)

COMPLETENESS_REPORT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "data_quality"
    / "listing_completeness_report.csv"
)


# ---------------------------------------------------------
# Data-loading functions
# ---------------------------------------------------------

@st.cache_data(
    show_spinner="Loading Airbnb market data..."
)
def load_dashboard_data(
    database_path: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load listing, monthly availability, and monthly review
    data from DuckDB.
    """
    connection = duckdb.connect(
        database_path,
        read_only=True
    )

    try:
        listings = connection.execute(
            """
            SELECT
                listing.listing_id,
                listing.listing_name,
                listing.property_type,
                listing.room_type,
                listing.accommodates,
                listing.bedrooms,
                listing.beds,
                listing.latitude,
                listing.longitude,
                listing.record_source,
                listing.has_detailed_record,

                host.host_id,
                host.host_name,
                host.host_is_superhost,
                host.host_portfolio_size,
                host.host_segment,

                neighbourhood.neighbourhood_name,

                facts.price,
                facts.minimum_nights,
                facts.maximum_nights,
                facts.number_of_reviews,
                facts.review_scores_rating,
                facts.availability_30,
                facts.availability_60,
                facts.availability_90,
                facts.availability_365,
                facts.estimated_occupancy_proxy,
                facts.estimated_availability_rate,
                facts.detailed_review_count,
                facts.host_tenure_years,
                facts.price_per_bedroom,
                facts.price_per_guest,
                facts.reviews_per_host_year

            FROM dim_listing AS listing

            LEFT JOIN dim_host AS host
                ON listing.host_key = host.host_key

            LEFT JOIN dim_neighbourhood AS neighbourhood
                ON listing.neighbourhood_key
                    = neighbourhood.neighbourhood_key

            INNER JOIN fact_listing_snapshot AS facts
                ON listing.listing_key
                    = facts.listing_key
            """
        ).fetchdf()

        monthly_availability = connection.execute(
            """
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
                dates.month_number
            """
        ).fetchdf()

        monthly_reviews = connection.execute(
            """
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
                dates.month_number
            """
        ).fetchdf()

    finally:
        connection.close()

    return (
        listings,
        monthly_availability,
        monthly_reviews
    )


@st.cache_data
def load_optional_csv(
    file_path: str
) -> pd.DataFrame:
    """
    Load an optional CSV output.
    """
    path = Path(file_path)

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def format_number(
    value: float | int,
    decimal_places: int = 0
) -> str:
    """
    Format a numerical metric while handling missing values.
    """
    if pd.isna(value):
        return "N/A"

    return f"{value:,.{decimal_places}f}"


def prepare_numeric_columns(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Standardise numerical fields after reading from DuckDB.
    """
    prepared = dataframe.copy()

    numeric_columns = [
        "accommodates",
        "bedrooms",
        "beds",
        "host_portfolio_size",
        "price",
        "minimum_nights",
        "maximum_nights",
        "number_of_reviews",
        "review_scores_rating",
        "availability_30",
        "availability_60",
        "availability_90",
        "availability_365",
        "estimated_occupancy_proxy",
        "estimated_availability_rate",
        "detailed_review_count",
        "host_tenure_years",
        "price_per_bedroom",
        "price_per_guest",
        "reviews_per_host_year"
    ]

    for column in numeric_columns:
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(
                prepared[column],
                errors="coerce"
            )

    return prepared


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

if not DATABASE_PATH.exists():
    st.error(
        "The DuckDB database was not found. "
        "Run `python -m src.build_database` first."
    )
    st.stop()

try:
    (
        listings,
        monthly_availability,
        monthly_reviews
    ) = load_dashboard_data(
        str(DATABASE_PATH)
    )

except Exception as error:
    st.error(
        f"Unable to load the DuckDB database: {error}"
    )

    st.info(
        "Close any notebook connection using the database "
        "and rebuild it with `python -m src.build_database`."
    )

    st.stop()

listings = prepare_numeric_columns(
    listings
)

listings["room_type"] = (
    listings["room_type"]
    .fillna("Unknown")
    .astype(str)
)

listings["property_type"] = (
    listings["property_type"]
    .fillna("Unknown")
    .astype(str)
)

listings["neighbourhood_name"] = (
    listings["neighbourhood_name"]
    .fillna("Unknown")
    .astype(str)
)

listings["host_segment"] = (
    listings["host_segment"]
    .fillna("Unknown")
    .astype(str)
)

listings["superhost_status"] = (
    listings["host_is_superhost"]
    .map({
        True: "Superhost",
        False: "Non-Superhost"
    })
    .fillna("Unknown")
)

statistics_results = load_optional_csv(
    str(STATISTICS_PATH)
)

validation_report = load_optional_csv(
    str(VALIDATION_REPORT_PATH)
)

completeness_report = load_optional_csv(
    str(COMPLETENESS_REPORT_PATH)
)


# ---------------------------------------------------------
# Sidebar and filters
# ---------------------------------------------------------

st.sidebar.title("Dashboard Controls")

page = st.sidebar.radio(
    "Select dashboard section",
    [
        "Market Overview",
        "Market Analysis",
        "Host Analysis",
        "Availability and Reviews",
        "Geographic Map",
        "Data Quality"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Market Filters")

price_values = listings["price"].dropna()

minimum_available_price = (
    float(price_values.min())
    if not price_values.empty
    else 0.0
)

maximum_available_price = (
    float(price_values.max())
    if not price_values.empty
    else 0.0
)

# Initialise widget state once. Empty multiselects mean "All".
st.session_state.setdefault("room_type_filter", [])
st.session_state.setdefault("neighbourhood_filter", [])
st.session_state.setdefault("host_segment_filter", [])
st.session_state.setdefault(
    "minimum_price_filter",
    minimum_available_price
)
st.session_state.setdefault(
    "maximum_price_filter",
    maximum_available_price
)
st.session_state.setdefault(
    "include_missing_price_filter",
    True
)


def reset_filters() -> None:
    """Reset all listing-level dashboard filters."""
    st.session_state["room_type_filter"] = []
    st.session_state["neighbourhood_filter"] = []
    st.session_state["host_segment_filter"] = []
    st.session_state["minimum_price_filter"] = minimum_available_price
    st.session_state["maximum_price_filter"] = maximum_available_price
    st.session_state["include_missing_price_filter"] = True


st.sidebar.button(
    "Reset all filters",
    use_container_width=True,
    on_click=reset_filters
)

st.sidebar.caption(
    "Leave a multiselect blank to include all values."
)

room_type_options = sorted(
    listings["room_type"]
    .dropna()
    .unique()
    .tolist()
)

selected_room_types = st.sidebar.multiselect(
    "Room type",
    options=room_type_options,
    key="room_type_filter",
    help="Leave blank to include all room types."
)

neighbourhood_options = sorted(
    listings["neighbourhood_name"]
    .dropna()
    .unique()
    .tolist()
)

selected_neighbourhoods = st.sidebar.multiselect(
    "Neighbourhood",
    options=neighbourhood_options,
    key="neighbourhood_filter",
    help="Leave blank to include all neighbourhoods."
)

host_segment_options = sorted(
    listings["host_segment"]
    .dropna()
    .unique()
    .tolist()
)

selected_host_segments = st.sidebar.multiselect(
    "Host segment",
    options=host_segment_options,
    key="host_segment_filter",
    help="Leave blank to include all host segments."
)

minimum_selected_price = st.sidebar.number_input(
    "Minimum price",
    min_value=0.0,
    step=10.0,
    key="minimum_price_filter"
)

maximum_selected_price = st.sidebar.number_input(
    "Maximum price",
    min_value=0.0,
    step=10.0,
    key="maximum_price_filter"
)

include_missing_prices = st.sidebar.checkbox(
    "Include listings with missing prices",
    key="include_missing_price_filter"
)

if maximum_selected_price < minimum_selected_price:
    st.sidebar.error(
        "Maximum price must be greater than or equal "
        "to minimum price."
    )
    st.stop()

room_type_mask = (
    listings["room_type"].isin(selected_room_types)
    if selected_room_types
    else pd.Series(True, index=listings.index)
)

neighbourhood_mask = (
    listings["neighbourhood_name"].isin(
        selected_neighbourhoods
    )
    if selected_neighbourhoods
    else pd.Series(True, index=listings.index)
)

host_segment_mask = (
    listings["host_segment"].isin(
        selected_host_segments
    )
    if selected_host_segments
    else pd.Series(True, index=listings.index)
)

filter_mask = (
    room_type_mask
    & neighbourhood_mask
    & host_segment_mask
)

price_filter_mask = listings["price"].between(
    minimum_selected_price,
    maximum_selected_price,
    inclusive="both"
)

if include_missing_prices:
    price_filter_mask = (
        price_filter_mask
        | listings["price"].isna()
    )

filtered_listings = listings[
    filter_mask
    & price_filter_mask
].copy()

st.sidebar.divider()

st.sidebar.metric(
    "Listings displayed",
    f"{len(filtered_listings):,}",
    help=(
        f"The complete dataset contains "
        f"{len(listings):,} listings."
    )
)

st.sidebar.caption(
    "Filters apply to listing-level dashboard sections. "
    "Monthly calendar and review trends remain market-wide."
)


# ---------------------------------------------------------
# Main heading
# ---------------------------------------------------------

st.title(
    "Singapore Airbnb Market Intelligence Dashboard"
)

st.caption(
    "Inside Airbnb dataset snapshot dated 29 June 2026"
)

if filtered_listings.empty:
    st.warning(
        "No listings match the selected filters."
    )
    st.stop()


# ---------------------------------------------------------
# Page 1: Market overview
# ---------------------------------------------------------

if page == "Market Overview":
    st.header("Market Overview")

    total_listings = (
        filtered_listings[
            "listing_id"
        ].nunique()
    )

    total_hosts = (
        filtered_listings[
            "host_id"
        ].nunique()
    )

    median_price = (
        filtered_listings[
            "price"
        ].median()
    )

    average_rating = (
        filtered_listings[
            "review_scores_rating"
        ].mean()
    )

    average_occupancy_proxy = (
        filtered_listings[
            "estimated_occupancy_proxy"
        ].mean() * 100
    )

    metric_columns = st.columns(5)

    metric_columns[0].metric(
        "Listings",
        format_number(total_listings)
    )

    metric_columns[1].metric(
        "Hosts",
        format_number(total_hosts)
    )

    metric_columns[2].metric(
        "Median price",
        format_number(
            median_price,
            2
        )
    )

    metric_columns[3].metric(
        "Average rating",
        format_number(
            average_rating,
            2
        )
    )

    metric_columns[4].metric(
        "Occupancy proxy",
        (
            f"{average_occupancy_proxy:.2f}%"
            if not pd.isna(
                average_occupancy_proxy
            )
            else "N/A"
        )
    )

    st.caption(
        "The occupancy figure is an estimated proxy based "
        "on unavailable calendar dates. It does not represent "
        "confirmed bookings."
    )

    st.divider()

    first_column, second_column = st.columns(2)

    with first_column:
        room_summary = (
            filtered_listings
            .groupby(
                "room_type",
                as_index=False
            )
            .agg(
                listing_count=(
                    "listing_id",
                    "nunique"
                ),
                median_price=(
                    "price",
                    "median"
                )
            )
            .sort_values(
                "median_price",
                ascending=False
            )
        )

        figure = px.bar(
            room_summary,
            x="room_type",
            y="median_price",
            title="Median Price by Room Type",
            labels={
                "room_type": "Room type",
                "median_price": "Median price"
            }
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    with second_column:
        neighbourhood_summary = (
            filtered_listings
            .groupby(
                "neighbourhood_name",
                as_index=False
            )
            .agg(
                listing_count=(
                    "listing_id",
                    "nunique"
                ),
                median_price=(
                    "price",
                    "median"
                )
            )
        )

        neighbourhood_summary = (
            neighbourhood_summary[
                neighbourhood_summary[
                    "listing_count"
                ] >= 10
            ]
            .dropna(
                subset=["median_price"]
            )
            .nlargest(
                10,
                "median_price"
            )
            .sort_values(
                "median_price",
                ascending=True
            )
        )

        figure = px.bar(
            neighbourhood_summary,
            x="median_price",
            y="neighbourhood_name",
            orientation="h",
            title=(
                "Top Neighbourhoods by Median Price"
            ),
            labels={
                "median_price": "Median price",
                "neighbourhood_name": (
                    "Neighbourhood"
                )
            }
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    st.subheader("Host Portfolio Composition")

    host_segment_summary = (
        filtered_listings[
            "host_segment"
        ]
        .value_counts(
            dropna=False
        )
        .rename_axis(
            "host_segment"
        )
        .reset_index(
            name="listing_count"
        )
    )

    figure = px.bar(
        host_segment_summary,
        x="host_segment",
        y="listing_count",
        title="Listings by Host Portfolio Segment",
        labels={
            "host_segment": "Host segment",
            "listing_count": (
                "Number of listings"
            )
        }
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    if not statistics_results.empty:
        st.subheader("Statistical Findings")

        statistics_display = statistics_results.copy()

        def format_p_value(value: float) -> str:
            """Format very small p-values in scientific notation."""
            if pd.isna(value):
                return "N/A"

            if value == 0:
                return "< 1e-300"

            return f"{value:.3e}"

        for column in [
            "first_group_median",
            "second_group_median",
            "median_difference",
            "rank_biserial_effect_size"
        ]:
            if column in statistics_display.columns:
                statistics_display[column] = (
                    pd.to_numeric(
                        statistics_display[column],
                        errors="coerce"
                    ).round(3)
                )

        for column in [
            "p_value",
            "holm_adjusted_p_value"
        ]:
            if column in statistics_display.columns:
                statistics_display[column] = (
                    pd.to_numeric(
                        statistics_display[column],
                        errors="coerce"
                    ).apply(format_p_value)
                )

        columns_to_show = [
            column
            for column in [
                "hypothesis",
                "first_group_median",
                "second_group_median",
                "median_difference",
                "holm_adjusted_p_value",
                "rank_biserial_effect_size",
                "effect_size_magnitude",
                "decision"
            ]
            if column in statistics_display.columns
        ]

        statistics_display = (
            statistics_display[
                columns_to_show
            ].rename(
                columns={
                    "hypothesis": "Hypothesis",
                    "first_group_median": "Group 1 Median",
                    "second_group_median": "Group 2 Median",
                    "median_difference": "Median Difference",
                    "holm_adjusted_p_value": "Adjusted P-value",
                    "rank_biserial_effect_size": "Effect Size",
                    "effect_size_magnitude": "Magnitude",
                    "decision": "Decision"
                }
            )
        )

        st.dataframe(
            statistics_display,
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------------------------
# Page 2: Market analysis
# ---------------------------------------------------------

elif page == "Market Analysis":
    st.header("Market Analysis")

    available_prices = (
        filtered_listings[
            "price"
        ]
        .dropna()
    )

    if available_prices.empty:
        st.warning(
            "The selected listings do not contain "
            "usable price values."
        )

    else:
        price_99th_percentile = (
            available_prices.quantile(
                0.99
            )
        )

        chart_prices = (
            filtered_listings[
                filtered_listings[
                    "price"
                ] <= price_99th_percentile
            ]
        )

        st.caption(
            "Price charts are displayed up to the 99th "
            "percentile for readability. Higher-price records "
            "remain in the analytical dataset."
        )

        first_column, second_column = (
            st.columns(2)
        )

        with first_column:
            figure = px.histogram(
                chart_prices,
                x="price",
                nbins=40,
                title=(
                    "Listing Price Distribution"
                ),
                labels={
                    "price": "Listing price"
                }
            )

            st.plotly_chart(
                figure,
                use_container_width=True
            )

        with second_column:
            figure = px.box(
                chart_prices,
                x="room_type",
                y="price",
                title=(
                    "Price Distribution by Room Type"
                ),
                labels={
                    "room_type": "Room type",
                    "price": "Listing price"
                },
                points=False
            )

            st.plotly_chart(
                figure,
                use_container_width=True
            )

    st.subheader(
        "Neighbourhood Market Summary"
    )

    neighbourhood_table = (
        filtered_listings
        .groupby(
            "neighbourhood_name",
            as_index=False
        )
        .agg(
            listing_count=(
                "listing_id",
                "nunique"
            ),
            unique_hosts=(
                "host_id",
                "nunique"
            ),
            median_price=(
                "price",
                "median"
            ),
            average_price=(
                "price",
                "mean"
            ),
            average_rating=(
                "review_scores_rating",
                "mean"
            ),
            average_occupancy_proxy=(
                "estimated_occupancy_proxy",
                "mean"
            )
        )
    )

    neighbourhood_table[
        "average_occupancy_proxy_percentage"
    ] = (
        neighbourhood_table[
            "average_occupancy_proxy"
        ] * 100
    )

    neighbourhood_table = (
        neighbourhood_table
        .drop(
            columns=[
                "average_occupancy_proxy"
            ]
        )
        .sort_values(
            "listing_count",
            ascending=False
        )
    )

    numeric_columns = [
        "median_price",
        "average_price",
        "average_rating",
        "average_occupancy_proxy_percentage"
    ]

    neighbourhood_table[
        numeric_columns
    ] = neighbourhood_table[
        numeric_columns
    ].round(2)

    st.dataframe(
        neighbourhood_table,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# Page 3: Host analysis
# ---------------------------------------------------------

elif page == "Host Analysis":
    st.header("Host and Supply Analysis")

    first_column, second_column = (
        st.columns(2)
    )

    with first_column:
        host_segment_data = (
            filtered_listings
            .groupby(
                "host_segment",
                as_index=False
            )
            .agg(
                listing_count=(
                    "listing_id",
                    "nunique"
                ),
                host_count=(
                    "host_id",
                    "nunique"
                ),
                median_price=(
                    "price",
                    "median"
                )
            )
            .sort_values(
                "listing_count",
                ascending=False
            )
        )

        figure = px.bar(
            host_segment_data,
            x="host_segment",
            y="listing_count",
            title=(
                "Listings by Host Segment"
            ),
            labels={
                "host_segment": "Host segment",
                "listing_count": (
                    "Listing count"
                )
            }
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    with second_column:
        superhost_data = (
            filtered_listings
            .groupby(
                "superhost_status",
                as_index=False
            )
            .agg(
                listing_count=(
                    "listing_id",
                    "nunique"
                ),
                median_price=(
                    "price",
                    "median"
                ),
                average_rating=(
                    "review_scores_rating",
                    "mean"
                )
            )
        )

        figure = px.bar(
            superhost_data,
            x="superhost_status",
            y="average_rating",
            title=(
                "Average Rating by Superhost Status"
            ),
            labels={
                "superhost_status": (
                    "Host status"
                ),
                "average_rating": (
                    "Average rating"
                )
            }
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )

    st.subheader(
        "Largest Hosts by Listing Count"
    )

    top_hosts = (
        filtered_listings
        .dropna(
            subset=["host_id"]
        )
        .groupby(
            [
                "host_id",
                "host_name",
                "host_segment",
                "superhost_status"
            ],
            dropna=False,
            as_index=False
        )
        .agg(
            listing_count=(
                "listing_id",
                "nunique"
            ),
            median_price=(
                "price",
                "median"
            ),
            average_rating=(
                "review_scores_rating",
                "mean"
            ),
            average_occupancy_proxy=(
                "estimated_occupancy_proxy",
                "mean"
            )
        )
        .sort_values(
            "listing_count",
            ascending=False
        )
        .head(20)
    )

    top_hosts[
        "average_occupancy_proxy_percentage"
    ] = (
        top_hosts[
            "average_occupancy_proxy"
        ] * 100
    )

    top_hosts = top_hosts.drop(
        columns=[
            "average_occupancy_proxy"
        ]
    )

    st.dataframe(
        top_hosts.round(2),
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# Page 4: Availability and reviews
# ---------------------------------------------------------

elif page == "Availability and Reviews":
    st.header("Availability and Review Trends")

    st.info(
        "Monthly trends are market-wide and are not "
        "affected by the listing filters."
    )

    monthly_availability[
        "month_start"
    ] = pd.to_datetime(
        dict(
            year=monthly_availability[
                "year_number"
            ].astype(int),
            month=monthly_availability[
                "month_number"
            ].astype(int),
            day=1
        )
    )

    monthly_reviews[
        "month_start"
    ] = pd.to_datetime(
        dict(
            year=monthly_reviews[
                "year_number"
            ].astype(int),
            month=monthly_reviews[
                "month_number"
            ].astype(int),
            day=1
        )
    )

    figure = px.line(
        monthly_availability,
        x="month_start",
        y="occupancy_proxy_percentage",
        markers=True,
        title=(
            "Monthly Estimated Occupancy Proxy"
        ),
        labels={
            "month_start": "Month",
            "occupancy_proxy_percentage": (
                "Occupancy proxy (%)"
            )
        }
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    st.caption(
        "Unavailable dates are used as a directional "
        "occupancy proxy. They may also represent host blocks, "
        "maintenance, personal use, or restrictions."
    )

    review_figure = px.line(
        monthly_reviews,
        x="month_start",
        y="review_count",
        title="Monthly Review Activity",
        labels={
            "month_start": "Month",
            "review_count": (
                "Number of reviews"
            )
        }
    )

    st.plotly_chart(
        review_figure,
        use_container_width=True
    )

    st.caption(
        "Review activity is an imperfect demand proxy because "
        "not every guest leaves a review."
    )

    st.subheader(
        "Filtered Neighbourhood Occupancy Proxy"
    )

    occupancy_neighbourhoods = (
        filtered_listings
        .groupby(
            "neighbourhood_name",
            as_index=False
        )
        .agg(
            listing_count=(
                "listing_id",
                "nunique"
            ),
            average_occupancy_proxy=(
                "estimated_occupancy_proxy",
                "mean"
            )
        )
    )

    occupancy_neighbourhoods = (
        occupancy_neighbourhoods[
            occupancy_neighbourhoods[
                "listing_count"
            ] >= 10
        ]
        .dropna(
            subset=[
                "average_occupancy_proxy"
            ]
        )
    )

    occupancy_neighbourhoods[
        "occupancy_proxy_percentage"
    ] = (
        occupancy_neighbourhoods[
            "average_occupancy_proxy"
        ] * 100
    )

    occupancy_neighbourhoods = (
        occupancy_neighbourhoods
        .nlargest(
            15,
            "occupancy_proxy_percentage"
        )
        .sort_values(
            "occupancy_proxy_percentage",
            ascending=True
        )
    )

    figure = px.bar(
        occupancy_neighbourhoods,
        x="occupancy_proxy_percentage",
        y="neighbourhood_name",
        orientation="h",
        title=(
            "Neighbourhood Occupancy Proxy"
        ),
        labels={
            "occupancy_proxy_percentage": (
                "Occupancy proxy (%)"
            ),
            "neighbourhood_name": (
                "Neighbourhood"
            )
        }
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )


# ---------------------------------------------------------
# Page 5: Geographic map
# ---------------------------------------------------------

elif page == "Geographic Map":
    st.header("Geographic Listing Distribution")

    map_data = (
        filtered_listings[
            [
                "listing_id",
                "latitude",
                "longitude",
                "listing_name",
                "room_type",
                "neighbourhood_name",
                "price"
            ]
        ]
        .dropna(
            subset=[
                "latitude",
                "longitude"
            ]
        )
        .copy()
    )

    map_data = map_data[
        map_data["latitude"].between(
            -90,
            90
        )
        & map_data["longitude"].between(
            -180,
            180
        )
    ]

    st.write(
        f"Listings shown on map: "
        f"**{len(map_data):,}**"
    )

    if map_data.empty:
        st.warning(
            "No valid coordinates are available for "
            "the selected filters."
        )

    else:
        streamlit_map_data = (
            map_data[
                [
                    "latitude",
                    "longitude"
                ]
            ]
            .rename(
                columns={
                    "latitude": "lat",
                    "longitude": "lon"
                }
            )
        )

        st.map(
            streamlit_map_data
        )

        st.subheader(
            "Mapped Listing Details"
        )

        st.dataframe(
            map_data[
                [
                    "listing_id",
                    "listing_name",
                    "room_type",
                    "neighbourhood_name",
                    "price",
                    "latitude",
                    "longitude"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "Geographic concentration does not by itself prove "
        "higher demand or profitability."
    )


# ---------------------------------------------------------
# Page 6: Data quality
# ---------------------------------------------------------

elif page == "Data Quality":
    st.header("Data Quality and Coverage")

    source_coverage = (
        listings[
            "record_source"
        ]
        .value_counts(
            dropna=False
        )
        .rename_axis(
            "record_source"
        )
        .reset_index(
            name="listing_count"
        )
    )

    source_coverage[
        "listing_share_percentage"
    ] = (
        source_coverage[
            "listing_count"
        ]
        / source_coverage[
            "listing_count"
        ].sum()
        * 100
    ).round(2)

    first_column, second_column = (
        st.columns(2)
    )

    with first_column:
        st.subheader(
            "Listing Source Coverage"
        )

        st.dataframe(
            source_coverage,
            use_container_width=True,
            hide_index=True
        )

    with second_column:
        st.subheader(
            "Important Missing Values"
        )

        quality_columns = [
            "price",
            "review_scores_rating",
            "host_id",
            "host_is_superhost",
            "estimated_occupancy_proxy",
            "detailed_review_count",
            "latitude",
            "longitude"
        ]

        missing_summary = pd.DataFrame({
            "column": quality_columns,
            "missing_count": [
                int(
                    listings[
                        column
                    ].isna().sum()
                )
                for column in quality_columns
            ],
            "missing_percentage": [
                round(
                    listings[
                        column
                    ].isna().mean() * 100,
                    2
                )
                for column in quality_columns
            ]
        })

        st.dataframe(
            missing_summary,
            use_container_width=True,
            hide_index=True
        )

    if not completeness_report.empty:
        st.subheader(
            "Completeness Warnings"
        )

        st.dataframe(
            completeness_report,
            use_container_width=True,
            hide_index=True
        )

    if not validation_report.empty:
        st.subheader(
            "Validation Rule Results"
        )

        st.dataframe(
            validation_report,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Known Limitations")

    st.markdown(
        """
        - Calendar unavailability does not confirm a booking.
        - The calendar dataset does not contain daily prices.
        - Missing prices are retained as explicit null values.
        - Review activity is an incomplete proxy for bookings.
        - The dataset represents a scraped snapshot rather than
          a complete transactional history.
        - Statistical relationships should not be interpreted
          as causal effects.
        """
    )