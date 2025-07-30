import calendar
import re
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Union

import pandas as pd

from app.logger import logger
from app.services.csv.constants import csv_constants


def get_dataframe(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load a CSV file into a DataFrame with error handling."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        logger.error("Failed to load CSV file %s: %s", file_path, e)
        raise


def _extract_response_content(response) -> str:
    """
    Extract content from LLM response, handling both string and list formats.

    Args:
        response: LLM response object.

    Returns:
        str: Extracted content string.
    """
    if isinstance(response.content, list):
        return "".join(str(item) for item in response.content).strip()
    return str(response.content).strip()


def is_month_name_column(series: pd.Series) -> bool:
    """Detects if the series contains month names like 'January', 'Feb', etc."""
    month_names = set(list(calendar.month_name[1:]) + list(calendar.month_abbr[1:]))
    return series.dropna().astype(str).str.strip().isin(month_names).mean() > 0.6


def detect_column_types(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """
    Detect and convert column types in a DataFrame (datetime, numeric, categorical).

    Performs automatic type detection and conversion for:
    - Object columns that might be datetime
    - Year columns that should be datetime
    - Ensures proper type categorization

    Args:
        df (pd.DataFrame): DataFrame to analyze and modify.

    Returns:
        Tuple[pd.DataFrame, Dict[str, List[str]]]:
            - Updated DataFrame with converted types
            - Dictionary mapping type names to column lists

    Raises:
        ValueError: If duplicate column names are found.
    """
    # Validate column uniqueness
    duplicate_cols = df.columns[df.columns.duplicated()].tolist()
    if duplicate_cols:
        raise ValueError(f"Duplicate columns found: {duplicate_cols}")

    logger.debug("Column dtypes before processing:")
    logger.debug("Types: %s", df.dtypes.to_dict())
    logger.debug("Sample data:\n%s", df.head())

    # Convert object columns that might be datetime
    for col in df.columns:
        if df[col].dtype == "object":
            sample = df[col].dropna().astype(str).head(10)

            if len(sample) == 0:
                continue

            # Check if it's a month name
            if is_month_name_column(sample):
                logger.debug("Converting column '%s' to datetime (month name)", col)
                df[col] = pd.to_datetime(
                    df[col].astype(str), format="%B", errors="coerce"
                )
                continue

            # Fallback: general datetime detection
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed_dates = pd.to_datetime(sample, errors="coerce")

            success_rate = parsed_dates.notna().mean()
            if success_rate > csv_constants.DATETIME_CONFIDENCE:
                logger.debug(
                    "Converting column '%s' to datetime (success rate: %.2f%%)",
                    col,
                    success_rate * 100,
                )
                df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            valid_years_ratio = df[col].between(1900, 2100).mean()

            is_year_name = col.lower() in ["year", "yr"] or re.search(
                r"\byear\b|\byr\b|\bfy\b", col.lower()
            )

            if valid_years_ratio > 0.9 and is_year_name:
                logger.debug("Converting year-like column '%s' to datetime", col)
                df[col] = pd.to_datetime(
                    df[col].astype(str), format="%Y", errors="coerce"
                )

    # Categorize columns by final types
    type_mapping = {
        "datetime": df.select_dtypes(
            include=["datetime", "datetime64[ns]"]
        ).columns.tolist(),
        "numeric": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical": df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist(),
    }

    logger.debug("Final column type mapping: %s", type_mapping)
    logger.info(type_mapping)
    return df, type_mapping


def get_outlier_columns(
    df: pd.DataFrame,
    types: Dict[str, List[str]],
    z_threshold: float = csv_constants.OUTLIER_Z_THRESHOLD,
) -> Dict[str, int]:
    """
    Detect numeric columns with outliers using Z-score method.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        types (Dict[str, List[str]]): Column type mapping.
        z_threshold (float): Z-score threshold for outlier detection.

    Returns:
        Dict[str, int]: Mapping of column names to outlier counts.
    """
    outlier_cols = {}

    for col in types.get("numeric", []):
        series = df[col].dropna()

        if len(series) == 0 or series.std() == 0:
            continue  # Skip empty or constant columns

        # Calculate Z-scores
        z_scores = abs((series - series.mean()) / series.std())
        outlier_count = (z_scores > z_threshold).sum()

        if outlier_count > 0:
            outlier_cols[col] = int(outlier_count)

    return outlier_cols


def get_high_cardinality_columns(
    df: pd.DataFrame,
    types: Dict[str, List[str]],
    threshold: int = csv_constants.HIGH_CARDINALITY_THRESHOLD,
) -> List[str]:
    """
    Detect categorical columns with high cardinality (too many unique values).

    High cardinality columns are problematic for:
    - Bar charts (too many bars)
    - Color encoding (too many categories)
    - Performance (memory usage)

    Args:
        df (pd.DataFrame): The dataset to analyze.
        types (Dict[str, List[str]]): Column type mapping.
        threshold (int): Maximum allowed unique values.

    Returns:
        List[str]: List of high cardinality column names.
    """
    high_card_cols = []

    for col in types.get("categorical", []):
        unique_count = df[col].nunique(dropna=True)
        if unique_count > threshold:
            high_card_cols.append(col)
            logger.debug(
                "Column '%s' has high cardinality: %d unique values", col, unique_count
            )

    return high_card_cols


def get_low_variance_columns(
    df: pd.DataFrame,
    types: Dict[str, List[str]],
    threshold: float = csv_constants.LOW_VARIANCE_THRESHOLD,
) -> List[str]:
    """
    Detect numeric columns with low variance (almost constant values).

    Low variance columns are usually not interesting for visualization
    as they don't show meaningful variation or patterns.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        types (Dict[str, List[str]]): Column type mapping.
        threshold (float): Minimum variance threshold.

    Returns:
        List[str]: List of low variance column names.
    """
    low_variance_cols = []

    for col in types.get("numeric", []):
        try:
            series = pd.to_numeric(df[col], errors="coerce").dropna()

            if len(series) == 0:
                continue

            variance = series.var()

            # Check if variance is a number and compare
            if (
                pd.notna(variance)
                and isinstance(variance, (int, float))
                and variance < threshold
            ):
                low_variance_cols.append(col)
                logger.debug("Column '%s' has low variance: %s", col, variance)

        except (TypeError, ValueError) as e:
            logger.debug("Could not calculate variance for column '%s': %s", col, e)
            continue

    return low_variance_cols


def extract_eda_stats(
    df: pd.DataFrame, types: Dict[str, List[str]]
) -> Tuple[Dict[str, int], List[str], List[str]]:
    """
    Extract comprehensive exploratory data analysis statistics.

    Runs multiple EDA utilities to identify data quality issues
    that affect visualization choices.

    Args:
        df (pd.DataFrame): The dataset to analyze.
        types (Dict[str, List[str]]): Column type mapping from detect_column_types.

    Returns:
        Tuple containing:
            - outlier_cols (Dict[str, int]): Column names mapped to outlier counts
            - high_card_cols (List[str]): High cardinality column names
            - low_var_cols (List[str]): Low variance column names
    """
    outlier_cols = get_outlier_columns(df, types)
    high_card_cols = get_high_cardinality_columns(df, types)
    low_var_cols = get_low_variance_columns(df, types)

    logger.debug(
        "EDA Stats - Outliers: %d, High-card: %d, Low-var: %d",
        len(outlier_cols),
        len(high_card_cols),
        len(low_var_cols),
    )

    return outlier_cols, high_card_cols, low_var_cols
