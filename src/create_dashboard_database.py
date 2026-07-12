from __future__ import annotations

from pathlib import Path

import duckdb


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

SOURCE_DATABASE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "database"
    / "airbnb_singapore.duckdb"
)

DASHBOARD_DATABASE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "database"
    / "airbnb_dashboard_serving.duckdb"
)


# ---------------------------------------------------------
# Database creation
# ---------------------------------------------------------

def create_dashboard_database() -> None:
    """
    Create a compact serving database for the deployed
    Streamlit dashboard.

    The complete analytical database remains unchanged.
    The serving database contains:

    1. All listing-level dashboard records
    2. Monthly availability calculated from the full calendar
    3. Monthly review activity calculated from all reviews
    4. Metadata showing the source and serving row counts
    """
    if not SOURCE_DATABASE_PATH.exists():
        raise FileNotFoundError(
            "The source analytical database was not found:\n"
            f"{SOURCE_DATABASE_PATH}\n\n"
            "Run `python -m src.build_database` first."
        )

    DASHBOARD_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if DASHBOARD_DATABASE_PATH.exists():
        DASHBOARD_DATABASE_PATH.unlink()

    source_database_sql_path = (
        SOURCE_DATABASE_PATH
        .as_posix()
        .replace("'", "''")
    )

    connection = duckdb.connect(
        str(DASHBOARD_DATABASE_PATH)
    )

    try:
        connection.execute(
            f"""
            ATTACH '{source_database_sql_path}'
            AS source_database
            (READ_ONLY)
            """
        )

        # -------------------------------------------------
        # Listing-level serving table
        # -------------------------------------------------

        connection.execute(
            """
            CREATE TABLE dashboard_listings AS

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

            FROM source_database.dim_listing AS listing

            LEFT JOIN source_database.dim_host AS host
                ON listing.host_key = host.host_key

            LEFT JOIN
                source_database.dim_neighbourhood
                AS neighbourhood

                ON listing.neighbourhood_key
                    = neighbourhood.neighbourhood_key

            INNER JOIN
                source_database.fact_listing_snapshot
                AS facts

                ON listing.listing_key
                    = facts.listing_key
            """
        )

        # -------------------------------------------------
        # Monthly availability serving table
        # -------------------------------------------------

        connection.execute(
            """
            CREATE TABLE
                dashboard_monthly_availability
            AS

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

            FROM
                source_database.fact_calendar
                AS calendar

            INNER JOIN
                source_database.dim_date
                AS dates

                ON calendar.date_key
                    = dates.date_key

            GROUP BY
                dates.year_number,
                dates.month_number,
                dates.month_name

            ORDER BY
                dates.year_number,
                dates.month_number
            """
        )

        # -------------------------------------------------
        # Monthly review serving table
        # -------------------------------------------------

        connection.execute(
            """
            CREATE TABLE
                dashboard_monthly_reviews
            AS

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

            FROM
                source_database.fact_reviews
                AS reviews

            INNER JOIN
                source_database.dim_date
                AS dates

                ON reviews.date_key
                    = dates.date_key

            GROUP BY
                dates.year_number,
                dates.month_number,
                dates.month_name

            ORDER BY
                dates.year_number,
                dates.month_number
            """
        )

        # -------------------------------------------------
        # Deployment lineage metadata
        # -------------------------------------------------

        connection.execute(
            """
            CREATE TABLE dashboard_metadata AS

            SELECT
                CURRENT_TIMESTAMP
                    AS generated_at,

                (
                    SELECT COUNT(*)
                    FROM source_database.dim_listing
                )
                    AS source_listing_rows,

                (
                    SELECT COUNT(*)
                    FROM dashboard_listings
                )
                    AS dashboard_listing_rows,

                (
                    SELECT COUNT(*)
                    FROM source_database.fact_calendar
                )
                    AS source_calendar_rows,

                (
                    SELECT COUNT(*)
                    FROM dashboard_monthly_availability
                )
                    AS dashboard_availability_rows,

                (
                    SELECT COUNT(*)
                    FROM source_database.fact_reviews
                )
                    AS source_review_rows,

                (
                    SELECT COUNT(*)
                    FROM dashboard_monthly_reviews
                )
                    AS dashboard_review_rows
            """
        )

        connection.execute(
            "CHECKPOINT"
        )

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        metadata = connection.execute(
            """
            SELECT *
            FROM dashboard_metadata
            """
        ).fetchdf()

        duplicate_listing_count = (
            connection.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        listing_id

                    FROM dashboard_listings

                    GROUP BY listing_id

                    HAVING COUNT(*) > 1
                )
                """
            )
            .fetchone()[0]
        )

        missing_listing_count = (
            connection.execute(
                """
                SELECT COUNT(*)
                FROM dashboard_listings
                WHERE listing_id IS NULL
                """
            )
            .fetchone()[0]
        )

        source_listing_rows = int(
            metadata.loc[
                0,
                "source_listing_rows"
            ]
        )

        dashboard_listing_rows = int(
            metadata.loc[
                0,
                "dashboard_listing_rows"
            ]
        )

        if (
            source_listing_rows
            != dashboard_listing_rows
        ):
            raise ValueError(
                "The dashboard listing population does "
                "not match the full analytical population."
            )

        if duplicate_listing_count > 0:
            raise ValueError(
                "Duplicate listing IDs were found in "
                "dashboard_listings."
            )

        if missing_listing_count > 0:
            raise ValueError(
                "Missing listing IDs were found in "
                "dashboard_listings."
            )

    finally:
        connection.close()


def display_database_summary() -> None:
    """
    Print row counts and file size for verification.
    """
    connection = duckdb.connect(
        str(DASHBOARD_DATABASE_PATH),
        read_only=True
    )

    try:
        metadata = connection.execute(
            """
            SELECT *
            FROM dashboard_metadata
            """
        ).fetchdf()

        table_counts = connection.execute(
            """
            SELECT
                'dashboard_listings'
                    AS table_name,

                COUNT(*)
                    AS row_count

            FROM dashboard_listings

            UNION ALL

            SELECT
                'dashboard_monthly_availability',
                COUNT(*)

            FROM dashboard_monthly_availability

            UNION ALL

            SELECT
                'dashboard_monthly_reviews',
                COUNT(*)

            FROM dashboard_monthly_reviews
            """
        ).fetchdf()

    finally:
        connection.close()

    file_size_mb = (
        DASHBOARD_DATABASE_PATH.stat().st_size
        / (1024 * 1024)
    )

    print("\nSource and serving layer validation")
    print("-" * 50)

    print(
        "Source listing rows:",
        f"{int(metadata.loc[0, 'source_listing_rows']):,}"
    )

    print(
        "Dashboard listing rows:",
        f"{int(metadata.loc[0, 'dashboard_listing_rows']):,}"
    )

    print(
        "Source calendar rows used:",
        f"{int(metadata.loc[0, 'source_calendar_rows']):,}"
    )

    print(
        "Monthly availability rows created:",
        f"{int(metadata.loc[0, 'dashboard_availability_rows']):,}"
    )

    print(
        "Source review rows used:",
        f"{int(metadata.loc[0, 'source_review_rows']):,}"
    )

    print(
        "Monthly review rows created:",
        f"{int(metadata.loc[0, 'dashboard_review_rows']):,}"
    )

    print("\nServing database tables")
    print("-" * 50)

    print(
        table_counts.to_string(
            index=False
        )
    )

    print(
        "\nServing database size:",
        f"{file_size_mb:.2f} MB"
    )

    if file_size_mb >= 100:
        raise ValueError(
            "The serving database remains too large "
            "for normal GitHub storage."
        )


def main() -> None:
    print(
        "Creating the Streamlit dashboard serving database"
    )

    print(
        "Source database:",
        SOURCE_DATABASE_PATH
    )

    create_dashboard_database()

    display_database_summary()

    print(
        "\nDashboard serving database created successfully:"
    )

    print(
        DASHBOARD_DATABASE_PATH
    )


if __name__ == "__main__":
    main()