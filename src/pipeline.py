from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from src.build_database import main as build_database
from src.run_cleaning import main as run_cleaning
from src.run_enrichment import main as run_enrichment
from src.run_sql_analysis import main as run_sql_analysis
from src.run_validation import main as run_validation


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

LOG_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "logs"
)


def configure_logging() -> Path:
    """
    Configure console and file logging for the full pipeline.
    """
    LOG_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    log_path = (
        LOG_DIRECTORY
        / f"pipeline_{timestamp}.log"
    )

    logger = logging.getLogger()

    logger.setLevel(
        logging.INFO
    )

    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    file_handler = logging.FileHandler(
        log_path,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )

    return log_path


def execute_step(
    step_name: str,
    step_function: Callable[[], None]
) -> None:
    """
    Execute one pipeline stage with timing and error logging.
    """
    logging.info(
        "Starting step: %s",
        step_name
    )

    start_time = time.perf_counter()

    try:
        step_function()

    except Exception:
        logging.exception(
            "Pipeline step failed: %s",
            step_name
        )

        raise

    elapsed_seconds = (
        time.perf_counter()
        - start_time
    )

    logging.info(
        "Completed step: %s in %.2f seconds",
        step_name,
        elapsed_seconds
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Singapore Airbnb "
            "data engineering pipeline."
        )
    )

    parser.add_argument(
        "--skip-sql",
        action="store_true",
        help=(
            "Build the engineering pipeline "
            "without executing analytical SQL."
        )
    )

    arguments = parser.parse_args()

    log_path = configure_logging()

    pipeline_start = time.perf_counter()

    logging.info(
        "Singapore Airbnb pipeline started"
    )

    logging.info(
        "Project root: %s",
        PROJECT_ROOT
    )

    steps: list[
        tuple[
            str,
            Callable[[], None]
        ]
    ] = [
        (
            "Cleaning and standardisation",
            run_cleaning
        ),
        (
            "Validation and quarantine",
            run_validation
        ),
        (
            "Enrichment and aggregation",
            run_enrichment
        ),
        (
            "DuckDB analytical model",
            build_database
        )
    ]

    if not arguments.skip_sql:
        steps.append(
            (
                "Analytical SQL outputs",
                run_sql_analysis
            )
        )

    try:
        for step_name, step_function in steps:
            execute_step(
                step_name,
                step_function
            )

    except Exception:
        total_seconds = (
            time.perf_counter()
            - pipeline_start
        )

        logging.error(
            "Pipeline failed after %.2f seconds",
            total_seconds
        )

        logging.error(
            "Review the log file: %s",
            log_path
        )

        raise

    total_seconds = (
        time.perf_counter()
        - pipeline_start
    )

    logging.info(
        "Pipeline completed successfully "
        "in %.2f seconds",
        total_seconds
    )

    logging.info(
        "Log file: %s",
        log_path
    )


if __name__ == "__main__":
    main()
    