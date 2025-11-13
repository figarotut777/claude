"""
#B8;8BK ?@8;>65=8O.
"""
from .text_similarity import (
    calculate_similarity,
    prepare_for_comparison,
    extract_brand_and_model,
    compare_attributes,
)
from .url_parser import (
    detect_marketplace,
    parse_marketplace_url,
    is_valid_marketplace_url,
)

__all__ = [
    "calculate_similarity",
    "prepare_for_comparison",
    "extract_brand_and_model",
    "compare_attributes",
    "detect_marketplace",
    "parse_marketplace_url",
    "is_valid_marketplace_url",
]
