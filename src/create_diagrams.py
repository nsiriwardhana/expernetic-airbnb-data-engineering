from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

DOCS_DIRECTORY = (
    PROJECT_ROOT
    / "docs"
)


def add_box(
    axis,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    details: list[str] | None = None,
    title_size: int = 11,
    detail_size: int = 8
) -> None:
    """
    Add a rounded rectangle with a title and optional details.
    """
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02",
        linewidth=1.4,
        facecolor="white",
        edgecolor="black"
    )

    axis.add_patch(box)

    axis.text(
        x + width / 2,
        y + height - 0.08,
        title,
        ha="center",
        va="top",
        fontsize=title_size,
        fontweight="bold"
    )

    if details:
        axis.text(
            x + 0.05,
            y + height - 0.25,
            "\n".join(details),
            ha="left",
            va="top",
            fontsize=detail_size,
            linespacing=1.25
        )


def add_arrow(
    axis,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str | None = None
) -> None:
    """
    Draw an arrow between two diagram components.
    """
    axis.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 1.5
        }
    )

    if label:
        axis.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            label,
            ha="center",
            va="center",
            fontsize=8,
            bbox={
                "facecolor": "white",
                "edgecolor": "none",
                "pad": 1
            }
        )


def create_architecture_diagram() -> None:
    """
    Create the complete data pipeline architecture diagram.
    """
    figure, axis = plt.subplots(
        figsize=(15, 8)
    )

    axis.set_xlim(0, 15)
    axis.set_ylim(0, 8)
    axis.axis("off")

    axis.set_title(
        "Singapore Airbnb Data Engineering Architecture",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    add_box(
        axis,
        0.4,
        5.7,
        2.2,
        1.3,
        "Inside Airbnb",
        [
            "listings.csv.gz",
            "calendar.csv.gz",
            "reviews.csv.gz",
            "summary files",
            "neighbourhood files"
        ]
    )

    add_box(
        axis,
        3.2,
        5.7,
        2.2,
        1.3,
        "Raw Layer",
        [
            "Original source files",
            "No manual changes",
            "data/raw/singapore/"
        ]
    )

    add_box(
        axis,
        6.0,
        5.7,
        2.2,
        1.3,
        "Cleaning Layer",
        [
            "Price conversion",
            "Date parsing",
            "Boolean conversion",
            "Text standardisation"
        ]
    )

    add_box(
        axis,
        8.8,
        5.7,
        2.2,
        1.3,
        "Validation Layer",
        [
            "Integrity checks",
            "Domain checks",
            "Foreign-key checks",
            "Quarantine handling"
        ]
    )

    add_box(
        axis,
        11.6,
        5.7,
        2.7,
        1.3,
        "Validated Data",
        [
            "Valid Parquet files",
            "Quarantined records",
            "Quality reports"
        ]
    )

    add_arrow(
        axis,
        (2.6, 6.35),
        (3.2, 6.35)
    )

    add_arrow(
        axis,
        (5.4, 6.35),
        (6.0, 6.35)
    )

    add_arrow(
        axis,
        (8.2, 6.35),
        (8.8, 6.35)
    )

    add_arrow(
        axis,
        (11.0, 6.35),
        (11.6, 6.35)
    )

    add_box(
        axis,
        1.0,
        3.0,
        2.7,
        1.5,
        "Enrichment",
        [
            "Calendar aggregation",
            "Review aggregation",
            "Occupancy proxy",
            "Host segmentation",
            "Derived measures"
        ]
    )

    add_box(
        axis,
        4.6,
        3.0,
        2.7,
        1.5,
        "DuckDB Star Schema",
        [
            "Listing dimension",
            "Host dimension",
            "Neighbourhood dimension",
            "Date dimension",
            "Three fact tables"
        ]
    )

    add_box(
        axis,
        8.2,
        3.0,
        2.7,
        1.5,
        "Analytics",
        [
            "Analytical SQL",
            "EDA notebooks",
            "Statistical testing",
            "CSV result exports"
        ]
    )

    add_box(
        axis,
        11.8,
        3.0,
        2.7,
        1.5,
        "Presentation",
        [
            "Streamlit dashboard",
            "Charts and tables",
            "Final PDF report",
            "GitHub repository"
        ]
    )

    add_arrow(
        axis,
        (12.95, 5.7),
        (2.35, 4.5),
        "Validated inputs"
    )

    add_arrow(
        axis,
        (3.7, 3.75),
        (4.6, 3.75)
    )

    add_arrow(
        axis,
        (7.3, 3.75),
        (8.2, 3.75)
    )

    add_arrow(
        axis,
        (10.9, 3.75),
        (11.8, 3.75)
    )

    add_box(
        axis,
        4.3,
        0.6,
        6.4,
        1.2,
        "Automation, Metadata, Logging and Testing",
        [
            "python -m src.pipeline",
            "Pipeline logs",
            "Data quality reports",
            "Schema checks",
            "pytest unit tests"
        ],
        title_size=12,
        detail_size=9
    )

    add_arrow(
        axis,
        (6.0, 3.0),
        (6.0, 1.8)
    )

    add_arrow(
        axis,
        (9.5, 3.0),
        (9.5, 1.8)
    )

    output_path = (
        DOCS_DIRECTORY
        / "architecture.png"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "Architecture diagram saved:",
        output_path
    )


def create_star_schema_diagram() -> None:
    """
    Create the DuckDB dimensional model diagram.
    """
    figure, axis = plt.subplots(
        figsize=(16, 10)
    )

    axis.set_xlim(0, 16)
    axis.set_ylim(0, 10)
    axis.axis("off")

    axis.set_title(
        "Singapore Airbnb Analytical Star Schema",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    add_box(
        axis,
        6.0,
        4.1,
        4.0,
        2.0,
        "dim_listing",
        [
            "PK listing_key",
            "NK listing_id",
            "FK host_key",
            "FK neighbourhood_key",
            "listing_name",
            "property_type",
            "room_type",
            "coordinates",
            "record_source"
        ],
        title_size=12
    )

    add_box(
        axis,
        0.5,
        6.8,
        3.3,
        2.0,
        "dim_host",
        [
            "PK host_key",
            "NK host_id",
            "host_name",
            "host_since",
            "host_is_superhost",
            "host_response_rate",
            "host_portfolio_size",
            "host_segment"
        ],
        title_size=12
    )

    add_box(
        axis,
        12.2,
        6.8,
        3.3,
        2.0,
        "dim_neighbourhood",
        [
            "PK neighbourhood_key",
            "neighbourhood_name",
            "city",
            "country"
        ],
        title_size=12
    )

    add_box(
        axis,
        6.2,
        7.0,
        3.6,
        2.0,
        "dim_date",
        [
            "PK date_key",
            "full_date",
            "day_number",
            "month_number",
            "month_name",
            "quarter_number",
            "year_number",
            "is_weekend"
        ],
        title_size=12
    )

    add_box(
        axis,
        0.4,
        1.0,
        4.4,
        2.2,
        "fact_listing_snapshot",
        [
            "FK listing_key",
            "FK snapshot_date_key",
            "price",
            "minimum_nights",
            "number_of_reviews",
            "review_scores_rating",
            "availability measures",
            "occupancy proxy",
            "derived listing measures"
        ],
        title_size=12
    )

    add_box(
        axis,
        5.8,
        1.0,
        4.4,
        2.2,
        "fact_calendar",
        [
            "FK listing_key",
            "FK date_key",
            "available",
            "minimum_nights",
            "maximum_nights",
            "Grain: listing per date"
        ],
        title_size=12
    )

    add_box(
        axis,
        11.2,
        1.0,
        4.4,
        2.2,
        "fact_reviews",
        [
            "PK review_id",
            "FK listing_key",
            "FK date_key",
            "reviewer_id",
            "review_length",
            "Grain: one review"
        ],
        title_size=12
    )

    add_arrow(
        axis,
        (3.8, 7.8),
        (6.0, 5.5),
        "host_key"
    )

    add_arrow(
        axis,
        (12.2, 7.8),
        (10.0, 5.5),
        "neighbourhood_key"
    )

    

    add_arrow(
        axis,
        (6.5, 4.1),
        (3.7, 3.2),
        "listing_key"
    )

    add_arrow(
        axis,
        (8.0, 4.1),
        (8.0, 3.2),
        "listing_key"
    )

    add_arrow(
        axis,
        (9.5, 4.1),
        (12.3, 3.2),
        "listing_key"
    )

    add_arrow(
        axis,
        (7.1, 7.0),
        (3.8, 3.2),
        "snapshot_date_key"
    )

    add_arrow(
        axis,
        (8.0, 7.0),
        (8.0, 3.2),
        "date_key"
    )

    add_arrow(
        axis,
        (8.9, 7.0),
        (12.2, 3.2),
        "date_key"
    )

    output_path = (
        DOCS_DIRECTORY
        / "star_schema.png"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "Star-schema diagram saved:",
        output_path
    )


def main() -> None:
    DOCS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    create_architecture_diagram()
    create_star_schema_diagram()

    print(
        "\nAll diagrams created successfully."
    )


if __name__ == "__main__":
    main()