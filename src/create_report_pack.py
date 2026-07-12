from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

REPORT_DIRECTORY = (
    PROJECT_ROOT
    / "report"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
)

DOCS_DIRECTORY = (
    PROJECT_ROOT
    / "docs"
)

REPORT_WORKBOOK_PATH = (
    REPORT_DIRECTORY
    / "report_inputs.xlsx"
)

REPORT_SUMMARY_PATH = (
    REPORT_DIRECTORY
    / "report_inputs.md"
)

REPORT_MANIFEST_PATH = (
    REPORT_DIRECTORY
    / "report_asset_manifest.csv"
)


TABLE_FILES = {
    "dataset_overview": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "dataset_overview.csv"
    ),
    "validation_report": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "validation_report.csv"
    ),
    "failed_validation_rules": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "failed_validation_rules.csv"
    ),
    "listing_completeness": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "listing_completeness_report.csv"
    ),
    "enrichment_coverage": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "enrichment_coverage_report.csv"
    ),
    "database_table_counts": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "database_table_counts.csv"
    ),
    "database_schema_checks": (
        OUTPUT_DIRECTORY
        / "data_quality"
        / "database_schema_checks.csv"
    ),
    "market_overview_eda": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "market_overview.csv"
    ),
    "room_type_summary": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "room_type_summary.csv"
    ),
    "neighbourhood_analysis": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "neighbourhood_analysis.csv"
    ),
    "host_segment_summary": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "host_segment_summary.csv"
    ),
    "host_concentration": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "host_listing_concentration.csv"
    ),
    "review_price_correlation": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "review_price_correlation.csv"
    ),
    "eda_findings": (
        OUTPUT_DIRECTORY
        / "tables"
        / "eda"
        / "eda_findings_summary.csv"
    ),
    "statistical_results": (
        OUTPUT_DIRECTORY
        / "tables"
        / "statistics"
        / "statistical_results.csv"
    ),
    "statistical_methodology": (
        OUTPUT_DIRECTORY
        / "tables"
        / "statistics"
        / "statistical_methodology.csv"
    ),
    "h1_group_summary": (
        OUTPUT_DIRECTORY
        / "tables"
        / "statistics"
        / "h1_group_summary.csv"
    ),
    "h2_group_summary": (
        OUTPUT_DIRECTORY
        / "tables"
        / "statistics"
        / "h2_group_summary.csv"
    ),
    "h3_group_summary": (
        OUTPUT_DIRECTORY
        / "tables"
        / "statistics"
        / "h3_group_summary.csv"
    ),
    "market_overview_sql": (
        OUTPUT_DIRECTORY
        / "tables"
        / "sql_analysis"
        / "market_overview.csv"
    ),
    "host_market_concentration_sql": (
        OUTPUT_DIRECTORY
        / "tables"
        / "sql_analysis"
        / "host_market_concentration.csv"
    ),
    "listing_source_coverage": (
        OUTPUT_DIRECTORY
        / "tables"
        / "sql_analysis"
        / "listing_source_coverage.csv"
    )
}


def load_available_tables() -> dict[str, pd.DataFrame]:
    """
    Load all report input tables that currently exist.
    """
    tables = {}

    for table_name, file_path in TABLE_FILES.items():
        if not file_path.exists():
            print(
                f"Missing optional table: "
                f"{file_path.relative_to(PROJECT_ROOT)}"
            )
            continue

        try:
            tables[table_name] = pd.read_csv(
                file_path
            )

        except Exception as error:
            print(
                f"Unable to read {file_path.name}: "
                f"{error}"
            )

    return tables


def safe_sheet_name(
    name: str
) -> str:
    """
    Create a valid Excel worksheet name.
    """
    invalid_characters = [
        "\\",
        "/",
        "*",
        "?",
        ":",
        "[",
        "]"
    ]

    cleaned_name = name

    for character in invalid_characters:
        cleaned_name = cleaned_name.replace(
            character,
            "_"
        )

    return cleaned_name[:31]


def write_excel_workbook(
    tables: dict[str, pd.DataFrame]
) -> None:
    """
    Save report tables into one Excel workbook.
    """
    with pd.ExcelWriter(
        REPORT_WORKBOOK_PATH,
        engine="openpyxl"
    ) as writer:
        for table_name, dataframe in tables.items():
            dataframe.to_excel(
                writer,
                sheet_name=safe_sheet_name(
                    table_name
                ),
                index=False
            )

    print(
        "Report workbook created:",
        REPORT_WORKBOOK_PATH
    )


def dataframe_to_text(
    dataframe: pd.DataFrame,
    maximum_rows: int = 20
) -> str:
    """
    Convert a DataFrame to readable fixed-width text.
    """
    if dataframe.empty:
        return "No records available."

    display_dataframe = (
        dataframe
        .head(maximum_rows)
        .copy()
    )

    return display_dataframe.to_string(
        index=False
    )


def write_markdown_summary(
    tables: dict[str, pd.DataFrame]
) -> None:
    """
    Create a readable report input summary.
    """
    sections = [
        "# Final Report Input Summary",
        "",
        "This file collects verified outputs from the Singapore "
        "Airbnb data engineering project.",
        "",
        "Dataset snapshot: 29 June 2026",
        ""
    ]

    for table_name, dataframe in tables.items():
        readable_title = (
            table_name
            .replace("_", " ")
            .title()
        )

        sections.extend([
            f"## {readable_title}",
            "",
            f"Rows available: {len(dataframe):,}",
            "",
            "```text",
            dataframe_to_text(
                dataframe
            ),
            "```",
            ""
        ])

    REPORT_SUMMARY_PATH.write_text(
        "\n".join(sections),
        encoding="utf-8"
    )

    print(
        "Report summary created:",
        REPORT_SUMMARY_PATH
    )


def collect_report_assets() -> pd.DataFrame:
    """
    Create a manifest of diagrams, charts, screenshots,
    notebooks, and documentation files.
    """
    search_locations = [
        DOCS_DIRECTORY,
        OUTPUT_DIRECTORY / "charts",
        PROJECT_ROOT / "notebooks"
    ]

    allowed_suffixes = {
        ".png",
        ".jpg",
        ".jpeg",
        ".ipynb",
        ".md",
        ".csv"
    }

    asset_rows = []

    for location in search_locations:
        if not location.exists():
            continue

        for file_path in location.rglob("*"):
            if not file_path.is_file():
                continue

            if (
                file_path.suffix.lower()
                not in allowed_suffixes
            ):
                continue

            asset_rows.append({
                "asset_name": file_path.name,
                "asset_type": (
                    file_path.suffix
                    .lower()
                    .replace(".", "")
                ),
                "relative_path": str(
                    file_path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "size_kb": round(
                    file_path.stat().st_size
                    / 1024,
                    2
                )
            })

    manifest = pd.DataFrame(
        asset_rows
    )

    if not manifest.empty:
        manifest = (
            manifest
            .sort_values(
                [
                    "asset_type",
                    "relative_path"
                ]
            )
            .reset_index(drop=True)
        )

    return manifest


def main() -> None:
    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Loading report input tables")

    tables = load_available_tables()

    if not tables:
        raise FileNotFoundError(
            "No report input tables were found. "
            "Run the pipeline and notebooks first."
        )

    print(
        f"Loaded {len(tables)} report tables"
    )

    write_excel_workbook(
        tables
    )

    write_markdown_summary(
        tables
    )

    manifest = collect_report_assets()

    manifest.to_csv(
        REPORT_MANIFEST_PATH,
        index=False
    )

    print(
        "Report asset manifest created:",
        REPORT_MANIFEST_PATH
    )

    print("\nReport pack completed successfully")

    print(
        "Tables in workbook:",
        len(tables)
    )

    print(
        "Assets in manifest:",
        len(manifest)
    )


if __name__ == "__main__":
    main()