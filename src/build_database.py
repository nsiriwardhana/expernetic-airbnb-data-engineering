from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

ENRICHED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "enriched"
)

VALIDATED_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validated"
)

DATABASE_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "database"
)

QUALITY_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "data_quality"
)

DATABASE_PATH = (
    DATABASE_DIRECTORY
    / "airbnb_singapore.duckdb"
)


def sql_path(path: Path) -> str:
    """
    Convert a Windows path into a form that can be safely
    used inside a DuckDB SQL statement.
    """
    return path.resolve().as_posix().replace(
        "'",
        "''"
    )


def create_staging_tables(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Load the validated and enriched Parquet datasets into
    DuckDB staging tables.
    """
    listing_path = sql_path(
        ENRICHED_DIRECTORY
        / "listing_enriched.parquet"
    )

    calendar_path = sql_path(
        VALIDATED_DIRECTORY
        / "calendar_valid.parquet"
    )

    reviews_path = sql_path(
        VALIDATED_DIRECTORY
        / "reviews_detailed_valid.parquet"
    )

    neighbourhood_path = sql_path(
        VALIDATED_DIRECTORY
        / "neighbourhoods_valid.parquet"
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE stg_listing_enriched AS
        SELECT *
        FROM read_parquet('{listing_path}')
        """
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE stg_calendar AS
        SELECT *
        FROM read_parquet('{calendar_path}')
        """
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE stg_reviews AS
        SELECT *
        FROM read_parquet('{reviews_path}')
        """
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE stg_neighbourhoods AS
        SELECT *
        FROM read_parquet('{neighbourhood_path}')
        """
    )


def create_dimensions(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Create the host, neighbourhood, listing, and date
    dimensions.
    """
    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_host AS
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY host_id
            ) AS host_key,

            host_id,

            MAX(host_name) AS host_name,

            MIN(host_since) AS host_since,

            MAX(host_is_superhost) AS host_is_superhost,

            MAX(host_response_rate) AS host_response_rate,

            MAX(host_acceptance_rate) AS host_acceptance_rate,

            MAX(host_portfolio_size) AS host_portfolio_size,

            MAX(host_segment) AS host_segment

        FROM stg_listing_enriched

        WHERE host_id IS NOT NULL

        GROUP BY host_id
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_neighbourhood AS
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY neighbourhood_cleansed
            ) AS neighbourhood_key,

            neighbourhood_cleansed
                AS neighbourhood_name,

            'Singapore' AS city,

            'Singapore' AS country

        FROM (
            SELECT DISTINCT
                neighbourhood_cleansed

            FROM stg_listing_enriched

            WHERE neighbourhood_cleansed
                IS NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_listing AS
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY listings.id
            ) AS listing_key,

            listings.id AS listing_id,

            hosts.host_key,

            neighbourhoods.neighbourhood_key,

            listings.name AS listing_name,

            listings.property_type,

            listings.room_type,

            listings.accommodates,

            listings.bedrooms,

            listings.beds,

            listings.latitude,

            listings.longitude,

            listings.record_source,

            listings.has_detailed_record

        FROM stg_listing_enriched AS listings

        LEFT JOIN dim_host AS hosts
            ON listings.host_id = hosts.host_id

        LEFT JOIN dim_neighbourhood
            AS neighbourhoods

            ON listings.neighbourhood_cleansed
                = neighbourhoods.neighbourhood_name
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE dim_date AS

        WITH all_dates AS (
            SELECT
                CAST(date AS DATE) AS full_date
            FROM stg_calendar
            WHERE date IS NOT NULL

            UNION

            SELECT
                CAST(date AS DATE) AS full_date
            FROM stg_reviews
            WHERE date IS NOT NULL

            UNION

            SELECT
                CAST(
                    analysis_snapshot_date AS DATE
                ) AS full_date
            FROM stg_listing_enriched
            WHERE analysis_snapshot_date IS NOT NULL
        )

        SELECT
            CAST(
                STRFTIME(
                    full_date,
                    '%Y%m%d'
                ) AS INTEGER
            ) AS date_key,

            full_date,

            EXTRACT(
                DAY FROM full_date
            ) AS day_number,

            EXTRACT(
                MONTH FROM full_date
            ) AS month_number,

            STRFTIME(
                full_date,
                '%B'
            ) AS month_name,

            EXTRACT(
                QUARTER FROM full_date
            ) AS quarter_number,

            EXTRACT(
                YEAR FROM full_date
            ) AS year_number,

            STRFTIME(
                full_date,
                '%A'
            ) AS day_name,

            CASE
                WHEN EXTRACT(
                    ISODOW FROM full_date
                ) IN (6, 7)
                THEN TRUE
                ELSE FALSE
            END AS is_weekend

        FROM all_dates

        ORDER BY full_date
        """
    )


def create_fact_tables(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Create listing snapshot, calendar, and review fact tables.
    """
    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_listing_snapshot AS
        SELECT
            listings.listing_key,

            dates.date_key
                AS snapshot_date_key,

            source.price,

            source.minimum_nights,

            source.maximum_nights,

            source.number_of_reviews,

            source.review_scores_rating,

            source.availability_30,

            source.availability_60,

            source.availability_90,

            source.availability_365,

            source.estimated_occupancy_proxy,

            source.estimated_availability_rate,

            source.detailed_review_count,

            source.host_tenure_years,

            source.price_per_bedroom,

            source.price_per_guest,

            source.reviews_per_host_year

        FROM stg_listing_enriched AS source

        INNER JOIN dim_listing AS listings
            ON source.id = listings.listing_id

        LEFT JOIN dim_date AS dates
            ON CAST(
                source.analysis_snapshot_date
                AS DATE
            ) = dates.full_date
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_calendar AS
        SELECT
            listings.listing_key,

            dates.date_key,

            calendar.available,

            calendar.minimum_nights,

            calendar.maximum_nights

        FROM stg_calendar AS calendar

        INNER JOIN dim_listing AS listings
            ON calendar.listing_id
                = listings.listing_id

        INNER JOIN dim_date AS dates
            ON CAST(
                calendar.date AS DATE
            ) = dates.full_date
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE fact_reviews AS
        SELECT
            reviews.id AS review_id,

            listings.listing_key,

            dates.date_key,

            reviews.reviewer_id,

            reviews.review_length

        FROM stg_reviews AS reviews

        INNER JOIN dim_listing AS listings
            ON reviews.listing_id
                = listings.listing_id

        INNER JOIN dim_date AS dates
            ON CAST(
                reviews.date AS DATE
            ) = dates.full_date
        """
    )


def create_metadata_table(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Record when each analytical table was created.
    """
    connection.execute(
        """
        CREATE OR REPLACE TABLE pipeline_table_metadata AS

        SELECT
            CURRENT_TIMESTAMP
                AS database_build_timestamp,

            table_name,

            estimated_size,

            column_count,

            index_count

        FROM duckdb_tables()

        WHERE table_name LIKE 'dim_%'
           OR table_name LIKE 'fact_%'
           OR table_name LIKE 'stg_%'
        """
    )


def create_indexes(
    connection: duckdb.DuckDBPyConnection
) -> None:
    """
    Create indexes for common dimension and fact joins.
    """
    index_statements = [
        """
        CREATE INDEX IF NOT EXISTS
        idx_dim_listing_listing_id
        ON dim_listing(listing_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS
        idx_dim_host_host_id
        ON dim_host(host_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS
        idx_dim_date_date_key
        ON dim_date(date_key)
        """,

        """
        CREATE INDEX IF NOT EXISTS
        idx_calendar_listing_key
        ON fact_calendar(listing_key)
        """,

        """
        CREATE INDEX IF NOT EXISTS
        idx_calendar_date_key
        ON fact_calendar(date_key)
        """,

        """
        CREATE INDEX IF NOT EXISTS
        idx_reviews_listing_key
        ON fact_reviews(listing_key)
        """
    ]

    for statement in index_statements:
        connection.execute(statement)


def run_schema_checks(
    connection: duckdb.DuckDBPyConnection
) -> pd.DataFrame:
    """
    Check uniqueness and foreign-key relationships.
    """
    checks = [
        (
            "Duplicate dim_listing listing_key",
            """
            SELECT COUNT(*)
            FROM (
                SELECT listing_key
                FROM dim_listing
                GROUP BY listing_key
                HAVING COUNT(*) > 1
            )
            """
        ),
        (
            "Duplicate dim_listing listing_id",
            """
            SELECT COUNT(*)
            FROM (
                SELECT listing_id
                FROM dim_listing
                GROUP BY listing_id
                HAVING COUNT(*) > 1
            )
            """
        ),
        (
            "Duplicate dim_host host_key",
            """
            SELECT COUNT(*)
            FROM (
                SELECT host_key
                FROM dim_host
                GROUP BY host_key
                HAVING COUNT(*) > 1
            )
            """
        ),
        (
            "Duplicate dim_date date_key",
            """
            SELECT COUNT(*)
            FROM (
                SELECT date_key
                FROM dim_date
                GROUP BY date_key
                HAVING COUNT(*) > 1
            )
            """
        ),
        (
            "Listing snapshot orphan listing keys",
            """
            SELECT COUNT(*)
            FROM fact_listing_snapshot AS facts
            LEFT JOIN dim_listing AS listings
                ON facts.listing_key
                    = listings.listing_key
            WHERE listings.listing_key IS NULL
            """
        ),
        (
            "Calendar orphan listing keys",
            """
            SELECT COUNT(*)
            FROM fact_calendar AS facts
            LEFT JOIN dim_listing AS listings
                ON facts.listing_key
                    = listings.listing_key
            WHERE listings.listing_key IS NULL
            """
        ),
        (
            "Calendar orphan date keys",
            """
            SELECT COUNT(*)
            FROM fact_calendar AS facts
            LEFT JOIN dim_date AS dates
                ON facts.date_key = dates.date_key
            WHERE dates.date_key IS NULL
            """
        ),
        (
            "Review orphan listing keys",
            """
            SELECT COUNT(*)
            FROM fact_reviews AS facts
            LEFT JOIN dim_listing AS listings
                ON facts.listing_key
                    = listings.listing_key
            WHERE listings.listing_key IS NULL
            """
        ),
        (
            "Review orphan date keys",
            """
            SELECT COUNT(*)
            FROM fact_reviews AS facts
            LEFT JOIN dim_date AS dates
                ON facts.date_key = dates.date_key
            WHERE dates.date_key IS NULL
            """
        )
    ]

    results = []

    for check_name, query in checks:
        issue_count = connection.execute(
            query
        ).fetchone()[0]

        results.append({
            "schema_check": check_name,
            "issue_count": int(issue_count),
            "passed": int(issue_count) == 0
        })

    return pd.DataFrame(results)


def get_table_counts(
    connection: duckdb.DuckDBPyConnection
) -> pd.DataFrame:
    """
    Return the number of records in every analytical table.
    """
    tables = [
        "dim_host",
        "dim_neighbourhood",
        "dim_listing",
        "dim_date",
        "fact_listing_snapshot",
        "fact_calendar",
        "fact_reviews"
    ]

    rows = []

    for table_name in tables:
        row_count = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM {table_name}
            """
        ).fetchone()[0]

        rows.append({
            "table_name": table_name,
            "row_count": int(row_count)
        })

    return pd.DataFrame(rows)


def main() -> None:
    print("Starting DuckDB database build")

    DATABASE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    QUALITY_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = duckdb.connect(
        str(DATABASE_PATH)
    )

    try:
        print("Creating staging tables")
        create_staging_tables(connection)

        print("Creating dimension tables")
        create_dimensions(connection)

        print("Creating fact tables")
        create_fact_tables(connection)

        print("Creating indexes")
        create_indexes(connection)

        print("Creating metadata table")
        create_metadata_table(connection)

        print("Running schema checks")
        schema_checks = run_schema_checks(
            connection
        )

        table_counts = get_table_counts(
            connection
        )

        schema_checks.to_csv(
            QUALITY_DIRECTORY
            / "database_schema_checks.csv",
            index=False
        )

        table_counts.to_csv(
            QUALITY_DIRECTORY
            / "database_table_counts.csv",
            index=False
        )

        print("\nDatabase table counts")
        print(
            table_counts.to_string(
                index=False
            )
        )

        print("\nSchema checks")
        print(
            schema_checks.to_string(
                index=False
            )
        )

        failed_checks = schema_checks[
            ~schema_checks["passed"]
        ]

        if not failed_checks.empty:
            raise ValueError(
                "One or more database schema "
                "checks failed."
            )

        print(
            "\nDuckDB database built successfully"
        )

        print(
            "Database location:",
            DATABASE_PATH
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()