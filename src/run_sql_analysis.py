from __future__ import annotations

import re
from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "database"
    / "airbnb_singapore.duckdb"
)

SQL_FILE_PATH = (
    PROJECT_ROOT
    / "sql"
    / "analysis_queries.sql"
)

SQL_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "sql_analysis"
)


def parse_named_queries(
    sql_text: str
) -> dict[str, str]:
    """
    Extract SQL queries marked with:

    -- QUERY: query_name
    """
    parts = re.split(
        r"(?m)^-- QUERY:\s*"
        r"([A-Za-z0-9_]+)\s*$",
        sql_text
    )

    queries = {}

    for index in range(
        1,
        len(parts),
        2
    ):
        query_name = parts[index].strip()

        query_sql = (
            parts[index + 1]
            .strip()
            .rstrip(";")
        )

        if query_sql:
            queries[query_name] = query_sql

    return queries


def main() -> None:
    print("Starting SQL analysis")

    SQL_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: "
            f"{DATABASE_PATH}"
        )

    if not SQL_FILE_PATH.exists():
        raise FileNotFoundError(
            f"SQL query file not found: "
            f"{SQL_FILE_PATH}"
        )

    sql_text = SQL_FILE_PATH.read_text(
        encoding="utf-8"
    )

    queries = parse_named_queries(
        sql_text
    )

    if not queries:
        raise ValueError(
            "No named SQL queries were found."
        )

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

    execution_results = []

    try:
        for query_name, query_sql in queries.items():
            print(
                f"Running query: {query_name}"
            )

            try:
                result = connection.execute(
                    query_sql
                ).fetchdf()

                output_path = (
                    SQL_OUTPUT_DIRECTORY
                    / f"{query_name}.csv"
                )

                result.to_csv(
                    output_path,
                    index=False
                )

                execution_results.append({
                    "query_name": query_name,
                    "status": "success",
                    "output_rows": len(result),
                    "output_file": str(
                        output_path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "error_message": None
                })

                print(
                    f"Saved {len(result):,} rows"
                )

            except Exception as error:
                execution_results.append({
                    "query_name": query_name,
                    "status": "failed",
                    "output_rows": 0,
                    "output_file": None,
                    "error_message": str(error)
                })

                print(
                    f"Query failed: {error}"
                )

        execution_report = pd.DataFrame(
            execution_results
        )

        execution_report.to_csv(
            SQL_OUTPUT_DIRECTORY
            / "sql_execution_report.csv",
            index=False
        )

        failed_queries = execution_report[
            execution_report[
                "status"
            ] == "failed"
        ]

        print("\nSQL execution report")

        print(
            execution_report[
                [
                    "query_name",
                    "status",
                    "output_rows"
                ]
            ].to_string(
                index=False
            )
        )

        if not failed_queries.empty:
            raise RuntimeError(
                f"{len(failed_queries)} SQL "
                "queries failed. Check "
                "sql_execution_report.csv."
            )

        print(
            "\nAll SQL queries completed "
            "successfully"
        )

        print(
            "Outputs saved to:",
            SQL_OUTPUT_DIRECTORY
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()