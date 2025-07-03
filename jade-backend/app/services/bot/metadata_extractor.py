"""
Service module for metadata extraction and enhancement.

Provides structured parsing logic to extract and enrich metadata
from regulatory rulebook documents, enabling more accurate
hierarchical indexing and search relevance.
"""

import re
from typing import List, Dict, Any
from logger import logger


class RulebookMetadataExtractor:
    """
    Extract structured metadata from CBB Rulebook documents.

    This class uses pattern matching and heuristics to extract and
    classify important information such as volume, module, chapter,
    section, dates, and regulatory context.
    """

    def __init__(self):
        # CBB Rulebook structure patterns
        self.volume_pattern = r"Volume\s+(\d+):\s*([^\n]+)"
        self.module_pattern = r"MODULE\s+([A-Z]{2,3}):\s*([^\n]+)"
        self.chapter_pattern = r"CHAPTER\s+([A-Z]{2,3}-[A-Z0-9]+):\s*([^\n]+)"
        self.section_pattern = (
            r"Section\s+([A-Z]{2,3}-[A-Z0-9]+\.[0-9]+):\s*Page\s+(\d+)\s+of\s+(\d+)"
        )
        self.paragraph_pattern = r"^([A-Z]{2,3}-[A-Z0-9]+\.[0-9]+\.[0-9]+)"

        # Document type patterns
        self.users_guide_pattern = r"Users?'?\s*Guide"
        self.date_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})"

        # Rule vs Guidance identification
        self.rule_indicators = ["must", "shall", "required", "obliged", "mandatory"]

    def extract_volume_info(self, text: str) -> Dict[str, Any]:
        """Extract volume number and type from document text."""
        volume_match = re.search(self.volume_pattern, text, re.IGNORECASE)
        if volume_match:
            logger.debug(
                f"Extracted Volume: {volume_match.group(1)}, Type: {self._determine_volume_type(volume_match.group(2))}"
            )
            return {
                "volume_number": volume_match.group(1),
                "volume_type": self._determine_volume_type(volume_match.group(2)),
            }
        return {}

    def extract_module_info(self, text: str) -> Dict[str, Any]:
        """Extract module code and category from document text."""
        module_match = re.search(self.module_pattern, text, re.IGNORECASE)
        if module_match:
            logger.debug(
                f"Extracted Module: {module_match.group(1)}, Category: {self._categorize_module(module_match.group(2))}"
            )
            return {
                "module_code": module_match.group(1),
                "module_category": self._categorize_module(module_match.group(2)),
            }
        return {}

    def extract_chapter_info(self, text: str) -> Dict[str, Any]:
        """Extract chapter reference and type from document text."""
        chapter_match = re.search(self.chapter_pattern, text, re.IGNORECASE)
        if chapter_match:
            logger.debug(
                f"Extracted Chapter: {chapter_match.group(1)}, Type: {self._determine_chapter_type(chapter_match.group(1))}"
            )
            return {
                "chapter_reference": chapter_match.group(1),
                "chapter_type": self._determine_chapter_type(chapter_match.group(1)),
            }
        return {}

    def extract_section_info(self, text: str) -> Dict[str, Any]:
        """Extract section reference and pagination from document text."""
        section_match = re.search(self.section_pattern, text, re.IGNORECASE)
        if section_match:
            logger.debug(
                f"Extracted Section: {section_match.group(1)}, Page: {section_match.group(2)}"
            )
            return {
                "section_reference": section_match.group(1),
                "page_number": int(section_match.group(2)),
                "total_pages": int(section_match.group(3)),
            }
        return {}

    def extract_date_info(self, text: str) -> Dict[str, Any]:
        """Extract most recent date from the document."""
        date_matches = re.findall(self.date_pattern, text)
        if date_matches:
            latest_date = max(
                date_matches, key=lambda x: (int(x[1]), self._month_to_number(x[0]))
            )
            logger.debug(f"Extracted Date: {latest_date[0]} {latest_date[1]}")
            return {
                "last_updated": f"{latest_date[0]} {latest_date[1]}",
                "update_month": latest_date[0],
                "update_year": int(latest_date[1]),
            }
        return {}

    def determine_content_type(self, text: str) -> str:
        """
        Determine if a document contains Rule or Guidance based on heuristics.

        Returns:
            str: One of "Rule", "Guidance", or "Unknown"
        """
        rule_score = sum(
            1 for indicator in self.rule_indicators if indicator.lower() in text.lower()
        )
        if rule_score >= 2:
            return "Rule"
        elif "guidance" in text.lower() or "may" in text.lower():
            return "Guidance"
        return "Unknown"

    def extract_regulatory_context(self, text: str) -> Dict[str, Any]:
        """Extract legal basis, instrument type, and applicable entities from text."""
        context = {}

        if "Article" in text and "CBB Law" in text:
            context["legal_basis"] = "CBB Law"
        if "Regulation" in text and "pursuant to" in text:
            context["instrument_type"] = "Regulation"
        elif "Directive" in text and "pursuant to" in text:
            context["instrument_type"] = "Directive"

        if "Islamic bank" in text.lower():
            context["applies_to"] = "Islamic Banks"
        elif "conventional bank" in text.lower():
            context["applies_to"] = "Conventional Banks"
        elif "licensee" in text.lower():
            context["applies_to"] = "All Licensees"

        if context:
            logger.debug(f"Extracted regulatory context: {context}")
        return context

    def _determine_volume_type(self, title: str) -> str:
        """Classify volume type based on title text."""
        title_lower = title.lower()
        if "islamic" in title_lower:
            return "Islamic Banking"
        elif "conventional" in title_lower:
            return "Conventional Banking"
        elif "insurance" in title_lower:
            return "Insurance"
        elif "investment" in title_lower:
            return "Investment Business"
        return "Other"

    def _categorize_module(self, title: str) -> str:
        """Categorize module based on key words in title."""
        title_lower = title.lower()
        if "user" in title_lower and "guide" in title_lower:
            return "Administrative"
        elif "capital" in title_lower or "prudential" in title_lower:
            return "Prudential"
        elif "conduct" in title_lower or "business" in title_lower:
            return "Business Standards"
        elif "reporting" in title_lower:
            return "Reporting"
        elif "enforcement" in title_lower:
            return "Enforcement"
        return "Other"

    def _determine_chapter_type(self, reference: str) -> str:
        """Determine chapter type from chapter code suffix."""
        if reference.endswith("-A"):
            return "Introduction"
        elif reference.split("-")[-1].isdigit():
            return "Substantive"
        return "Other"

    def _month_to_number(self, month: str) -> int:
        """Convert English month name to its numeric value."""
        months = {
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12,
        }
        return months.get(month, 0)


def determine_hierarchy_level(metadata: Dict[str, Any]) -> str:
    """
    Determine the hierarchical level of a document or node based on its metadata.

    Args:
        metadata (dict): Metadata dictionary containing keys like volume_number, chapter_reference, etc.

    Returns:
        str: One of "Volume", "Module", "Chapter", "Section", or "Document".
    """
    if metadata.get("volume_number"):
        if metadata.get("section_reference"):
            return "Section"
        elif metadata.get("chapter_reference"):
            return "Chapter"
        elif metadata.get("module_code"):
            return "Module"
        else:
            return "Volume"
    return "Document"


def generate_search_tags(metadata: Dict[str, Any], text: str) -> List[str]:
    """
    Generate a list of semantic tags to improve retrieval and filtering.

    Args:
        metadata (dict): Extracted metadata from the document.
        text (str): Raw text content of the document.

    Returns:
        List[str]: A list of relevant tags.
    """
    tags = []

    if metadata.get("volume_type"):
        tags.append(metadata["volume_type"])
    if metadata.get("module_category"):
        tags.append(metadata["module_category"])
    if metadata.get("content_type"):
        tags.append(metadata["content_type"])
    if metadata.get("applies_to"):
        tags.append(metadata["applies_to"])
    if metadata.get("instrument_type"):
        tags.append(metadata["instrument_type"])

    key_terms = [
        "capital",
        "risk",
        "compliance",
        "reporting",
        "licensing",
        "governance",
    ]
    for term in key_terms:
        if term in text.lower():
            tags.append(term.title())

    return list(set(tags))  # Remove duplicates


def calculate_importance_score(metadata: Dict[str, Any], text: str) -> float:
    """
    Calculate a regulatory importance score between 0.0 and 1.0.

    Args:
        metadata (dict): Extracted metadata for a document or node.
        text (str): The text content of the node.

    Returns:
        float: Importance score based on rule status, recency, legal references, etc.
    """
    score = 0.0

    if metadata.get("content_type") == "Rule":
        score += 0.3

    current_year = 2025
    if metadata.get("update_year", 0) >= (current_year - 5):
        score += 0.2

    if (
        "enforcement" in text.lower()
        or "penalty" in text.lower()
        or "sanction" in text.lower()
    ):
        score += 0.2

    if metadata.get("module_category") == "Prudential":
        score += 0.2

    if metadata.get("legal_basis"):
        score += 0.1

    return min(score, 1.0)


def enhance_node_metadata(node: Any, extractor: RulebookMetadataExtractor) -> None:
    """
    Enrich a LlamaIndex node with additional metadata.

    Args:
        node (Any): A node object with `text` and `metadata` attributes.
        extractor (RulebookMetadataExtractor): Instance for extracting content-based metadata.
    """
    if hasattr(node, "metadata") and hasattr(node, "text"):
        node.metadata["node_content_type"] = extractor.determine_content_type(node.text)
        node.metadata["node_length"] = len(node.text)
        node.metadata["node_id"] = getattr(node, "node_id", "unknown")

        paragraph_matches = re.findall(
            r"([A-Z]{2,3}-[A-Z0-9]+\.[0-9]+\.[0-9]+)", node.text
        )
        if paragraph_matches:
            node.metadata["paragraph_references"] = list(set(paragraph_matches))
