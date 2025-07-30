"""
CSV chart suggestion service for generating visualization recommendations.

Provides functions for column type detection, basic chart generation,
AI-enhanced chart curation, and metadata enrichment.
"""

import ast
import json
import re
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from langchain_aws import ChatBedrock

from app.config.settings import settings
from app.logger import logger
from app.services.csv.constants import csv_constants
from app.services.csv.utils import (
    _extract_response_content,
    detect_column_types,
    extract_eda_stats,
    get_dataframe,
)

llm = ChatBedrock(
    model=settings.LLM_MODEL,
    region=settings.AWS_REGION,
    streaming=True,
)


def suggest_basic_charts(
    df: pd.DataFrame, types: Dict[str, List[str]]
) -> List[Dict[str, Any]]:
    """
    Generate basic chart suggestions based on column types and data characteristics.

    Creates suggestions for:
    - Line charts for datetime vs numeric trends
    - Histograms for numeric distributions
    - Bar charts for categorical data (excluding high cardinality)

    Args:
        df (pd.DataFrame): The dataset to analyze.
        types (Dict[str, List[str]]): Column type mapping from detect_column_types.

    Returns:
        List[Dict[str, Any]]: List of chart configuration dictionaries.
    """
    suggestions = []
    outlier_cols, high_card_cols, low_var_cols = extract_eda_stats(df, types)

    # LINE CHARTS – for datetime trends
    for dt_col in types["datetime"]:
        for numeric_col in types["numeric"]:
            if numeric_col in low_var_cols:
                continue  # Skip low variance columns

            suggestions.append(
                {
                    "x": dt_col,
                    "y": [numeric_col],
                    "type": "line",
                    "title": f"{numeric_col} over {dt_col}",
                }
            )

        # Multi-line charts for related metrics
        if len(types["numeric"]) >= 3:
            for combo in combinations(types["numeric"], 3):
                if any(col in low_var_cols for col in combo):
                    continue
                suggestions.append(
                    {
                        "x": dt_col,
                        "y": list(combo),
                        "type": "line",
                        "title": f"{', '.join(combo)} over {dt_col}",
                    }
                )

    # HISTOGRAMS – distributions for numeric columns
    for col in types["numeric"]:
        if col in low_var_cols and col not in outlier_cols:
            continue  # Skip boring low-variance columns unless they have outliers

        title = f"Distribution of {col}"
        if col in outlier_cols:
            title += " (contains outliers)"

        suggestions.append({"y": [col], "type": "histogram", "title": title})

    # BAR CHARTS – for categorical comparisons
    for col in types["categorical"]:
        if col in high_card_cols:
            continue  # Skip high cardinality columns

        suggestions.append({"x": col, "type": "bar", "title": f"Distribution of {col}"})

    logger.info(suggestions)

    return suggestions


async def suggest_ai_charts(
    df: pd.DataFrame, inferred_charts: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Use LLM to curate and improve chart suggestions for a CSV file.

    Takes basic chart suggestions and uses AI to:
    - Filter out redundant or low-value charts
    - Improve titles and descriptions
    - Add new insights-driven suggestions
    - Consider data quality issues (high cardinality, outliers, etc.)

    Args:
        df (pd.DataFrame): The CSV data as a DataFrame.
        inferred_charts (List[Dict[str, Any]]): List of candidate chart suggestions.

    Returns:
        List[Dict[str, Any]]: Final curated chart suggestions with enriched metadata.
    """
    if df.empty or not inferred_charts:
        return []

    try:
        # Prepare data sample and metadata
        sample = df.head(10).to_csv(index=False)
        chart_json = json.dumps(inferred_charts, indent=2)

        _, types = detect_column_types(df)
        outlier_cols, high_card_cols, low_var_cols = extract_eda_stats(df, types)

        # Build EDA insights for the prompt
        eda_insights = []
        if high_card_cols:
            eda_insights.append(
                f"- High-cardinality columns (avoid for x-axis in bar charts): {', '.join(high_card_cols)}"
            )
        if low_var_cols:
            eda_insights.append(
                f"- Low-variance columns (avoid as y-values): {', '.join(low_var_cols)}"
            )
        if outlier_cols:
            eda_insights.append(
                f"- Columns with outliers (highlight in distributions): {', '.join(outlier_cols.keys())}"
            )

        eda_summary = (
            "\n".join(eda_insights)
            if eda_insights
            else "- No significant data quality issues detected"
        )

        # Construct AI prompt
        prompt = f"""
You are a data visualization expert. Analyze this dataset sample and curate the most insightful charts for exploratory data analysis.

Dataset Sample:
{sample}

Candidate Chart Configurations:
{chart_json}

Data Quality Insights:
{eda_summary}

STRICT REQUIREMENTS:
1. Use only the following chart types: "bar", "line", "histogram"
2. Bar chart x-axis must be a categorical column (e.g. status, department)
3. Never use numeric IDs or name-like fields (e.g. Employee_ID, Product_ID, Name) as x-axis
4. Histograms must use exactly ONE numeric column
5. Line charts must use datetime or ordered numeric x-axis (e.g. Month, Year)

TASKS:
- Select only valuable and non-redundant charts
- Improve titles to make them more insightful and clear
- Add 1–2 new charts only if there's a clear missing pattern
- Consider data quality when deciding: skip charts that are hard to read or meaningless

Output must be a valid JSON array of chart configs with fields:
"x", "y", "type", "title"

DO NOT include scatter, area, pie, or any unsupported chart types.
DO NOT include markdown or any explanation — just return JSON.
"""

        response = await llm.ainvoke(input=prompt)
        raw_content = _extract_response_content(response)

        # Clean and parse response
        cleaned = re.sub(r"^```(?:json)?\n?|\n?```$", "", raw_content.strip())

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(cleaned)
            except (ValueError, SyntaxError):
                logger.warning(
                    "Failed to parse AI chart suggestions, returning basic suggestions"
                )
                return inferred_charts

    except (json.JSONDecodeError, ValueError, SyntaxError) as e:
        logger.error("Error in AI chart suggestion: %s", e)
        return inferred_charts


async def get_all_chart_suggestions(
    file_path: Union[str, Path],
) -> List[Dict[str, Any]]:
    """
    Generate comprehensive chart suggestions for a CSV file using both rule-based and AI approaches.

    Process:
    1. Load and analyze the CSV data
    2. Detect column types and data characteristics
    3. Generate basic chart suggestions using rules
    4. Enhance suggestions using AI
    5. Enrich with metadata (column types, data insights)

    Args:
        file_path (Union[str, Path]): Path to the CSV file.

    Returns:
        List[Dict[str, Any]]: Enhanced chart suggestions with metadata including:
            - x, y, type, title: Basic chart configuration
            - x_type, y_types: Data type information
            - Additional metadata for rendering

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        ValueError: If the CSV file is corrupted or empty.
    """
    try:
        df = get_dataframe(file_path)

        if df.empty:
            logger.warning("CSV file %s is empty", file_path)
            return []

        df, types = detect_column_types(df)

        # Generate basic suggestions
        basic_suggestions = suggest_basic_charts(df, types)

        if not basic_suggestions:
            logger.warning("No basic chart suggestions generated")
            return []

        # Enhance with AI
        curated_suggestions = await suggest_ai_charts(df, basic_suggestions)

        # Enrich with metadata
        enriched_charts = []
        for chart in curated_suggestions:
            enriched_chart = _enrich_chart_metadata(chart, types, df)
            enriched_charts.append(enriched_chart)

        logger.info(
            "Generated %d chart suggestions for %s", len(enriched_charts), file_path
        )
        return enriched_charts

    except (FileNotFoundError, ValueError) as e:
        logger.error("Error generating chart suggestions for %s: %s", file_path, e)
        raise


def suggest_aggregation(y_keys: list[str]) -> str:
    """
    Prefer 'sum' when it's clearly a summable field (e.g. money, counts, totals).
    Otherwise, default to 'avg'.
    """
    for y in y_keys:
        name = y.lower()
        if any(kw in name for kw in csv_constants.SUM_KEYWORDS):
            return "sum"
    return "avg"


def infer_x_format_hint(series: pd.Series) -> Optional[str]:
    if not pd.api.types.is_datetime64_any_dtype(series):
        return None
    months = series.dt.month.nunique()
    days = series.dt.day.nunique()
    if months == 1 and days == 1:
        return "year"
    if days == 1:
        return "month"
    return "date"


def _enrich_chart_metadata(
    chart: Dict[str, Any], types: Dict[str, List[str]], df: pd.DataFrame
) -> Dict[str, Any]:
    # Fix missing y field for bar charts
    if chart["type"] == "bar" and "y" not in chart:
        chart["y"] = ["Count"]

    chart["y"] = [chart["y"]] if isinstance(chart["y"], str) else (chart["y"] or [])

    # Determine type info
    x_type = None
    if chart.get("x"):
        x_type = next((k for k, cols in types.items() if chart["x"] in cols), "unknown")

    y_types = []
    for y in chart["y"]:
        if y == "Count":
            y_types.append("numeric")
        else:
            y_type = next((k for k, cols in types.items() if y in cols), "unknown")
            y_types.append(y_type)

    # Enrich metadata
    chart["x_type"] = x_type
    chart["y_types"] = y_types

    if chart["type"] == "line" and chart.get("x") in df.columns:
        x_vals = df[chart["x"]]
        is_grouped = bool(x_vals.duplicated().any())  # <-- FIXED
        chart["grouped"] = is_grouped
        chart["aggregation"] = suggest_aggregation(chart["y"]) if is_grouped else None
    else:
        chart["grouped"] = False
        chart["aggregation"] = None

    # Set xFormatHint if datetime
    if x_type == "datetime":
        x_series = df[chart["x"]]
        chart["xFormatHint"] = infer_x_format_hint(x_series)
    else:
        chart["xFormatHint"] = None

    return chart
