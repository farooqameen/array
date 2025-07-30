from pydantic import Field
from pydantic_settings import BaseSettings


class CSVChatConstants(BaseSettings):
    """
    Constants for CSV chat service.
    """

    TOKEN_ESTIMATION_RATIO: int = Field(
        4, description="Characters per token approximation"
    )
    DEFAULT_CHUNK_SIZE: int = Field(
        512, description="Default chunk size for tokenization"
    )
    DEFAULT_MIN_ROWS: int = Field(3, description="Minimum rows per chunk")
    DEFAULT_OVERLAP_ROWS: int = Field(
        2, description="Number of overlapping rows between chunks"
    )
    HIGH_CARDINALITY_THRESHOLD: int = Field(
        50, description="Threshold for high cardinality columns"
    )
    LOW_VARIANCE_THRESHOLD: float = Field(
        1e-5, description="Threshold for low variance columns"
    )
    OUTLIER_Z_THRESHOLD: float = Field(
        3.0, description="Z-score threshold for outlier detection"
    )

    SUM_KEYWORDS: set = Field(
        {
            "amount",
            "total",
            "revenue",
            "cost",
            "sales",
            "spend",
            "expense",
            "price",
            "profit",
            "income",
            "value",
            "quantity",
            "count",
        }
    )

    DATETIME_CONFIDENCE: float = Field(
        0.6, description="Confidence threshold for datetime detection"
    )


# Singleton instance for use in other modules
csv_constants = CSVChatConstants()
