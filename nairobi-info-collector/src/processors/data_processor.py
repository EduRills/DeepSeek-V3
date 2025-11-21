"""Data processor for cleaning, verifying, and enriching collected information."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from src.models import InformationItem, Category, ReliabilityLevel
from src.utils import get_logger, TextProcessor


class DataProcessor:
    """
    Process and verify collected information.

    Responsibilities:
    - Deduplicate items
    - Verify and score items
    - Filter by relevance and recency
    - Enrich with additional metadata
    """

    def __init__(self, min_relevance_score: float = 0.3, max_age_hours: int = 72):
        """
        Initialize data processor.

        Args:
            min_relevance_score: Minimum relevance score for items
            max_age_hours: Maximum age of items in hours
        """
        self.min_relevance_score = min_relevance_score
        self.max_age_hours = max_age_hours

        self.logger = get_logger(self.__class__.__name__)
        self.text_processor = TextProcessor()

    def process(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Process a list of information items.

        Args:
            items: Raw list of items

        Returns:
            Processed and filtered list of items
        """
        self.logger.info(f"Processing {len(items)} items")

        # Step 1: Remove duplicates
        items = self.deduplicate(items)
        self.logger.info(f"After deduplication: {len(items)} items")

        # Step 2: Filter by relevance
        items = self.filter_by_relevance(items)
        self.logger.info(f"After relevance filter: {len(items)} items")

        # Step 3: Filter by recency
        items = self.filter_by_recency(items)
        self.logger.info(f"After recency filter: {len(items)} items")

        # Step 4: Enrich items
        items = self.enrich_items(items)

        # Step 5: Sort by relevance and timestamp
        items = self.sort_items(items)

        self.logger.info(f"Processing complete: {len(items)} items")
        return items

    def deduplicate(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Remove duplicate items based on title and source similarity.

        Args:
            items: List of items

        Returns:
            Deduplicated list
        """
        seen = {}
        unique_items = []

        for item in items:
            # Create a key based on normalized title
            key = self._normalize_text(item.title)

            if key not in seen:
                seen[key] = item
                unique_items.append(item)
            else:
                # If duplicate found, keep the one with higher reliability
                existing = seen[key]
                if self._compare_reliability(item, existing) > 0:
                    # Replace with higher reliability item
                    unique_items.remove(existing)
                    unique_items.append(item)
                    seen[key] = item

        return unique_items

    def filter_by_relevance(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Filter items by relevance score.

        Args:
            items: List of items

        Returns:
            Filtered list
        """
        return [
            item for item in items
            if item.relevance_score >= self.min_relevance_score
        ]

    def filter_by_recency(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Filter items by recency.

        Args:
            items: List of items

        Returns:
            Filtered list containing only recent items
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=self.max_age_hours)

        return [
            item for item in items
            if item.timestamp >= cutoff_time
        ]

    def enrich_items(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Enrich items with additional metadata and analysis.

        Args:
            items: List of items

        Returns:
            Enriched items
        """
        for item in items:
            # Add impact level based on relevance and category
            item.impact_level = self._calculate_impact_level(item)

            # Ensure tags are populated
            if not item.tags:
                full_text = f"{item.title} {item.summary}"
                item.tags = self.text_processor.extract_keywords(full_text)

            # Add age metadata
            age_hours = (datetime.utcnow() - item.timestamp).total_seconds() / 3600
            item.metadata['age_hours'] = round(age_hours, 2)

            # Add recency indicator
            if age_hours < 1:
                item.metadata['recency'] = 'just_now'
            elif age_hours < 6:
                item.metadata['recency'] = 'recent'
            elif age_hours < 24:
                item.metadata['recency'] = 'today'
            elif age_hours < 48:
                item.metadata['recency'] = 'yesterday'
            else:
                item.metadata['recency'] = 'older'

        return items

    def sort_items(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Sort items by importance (relevance score, recency, reliability).

        Args:
            items: List of items

        Returns:
            Sorted list
        """
        def sort_key(item: InformationItem) -> tuple:
            # Sort by: category priority, relevance, recency
            category_priority = self._get_category_priority(item.category)
            reliability_score = self._get_reliability_score(item.reliability)
            recency_score = 1.0 / (1 + (datetime.utcnow() - item.timestamp).total_seconds() / 3600)

            # Combined score
            combined_score = (
                category_priority * 0.3 +
                item.relevance_score * 0.4 +
                reliability_score * 0.1 +
                recency_score * 0.2
            )

            return (-combined_score, item.timestamp)

        return sorted(items, key=sort_key)

    def get_statistics(self, items: List[InformationItem]) -> Dict[str, Any]:
        """
        Calculate statistics about the collected items.

        Args:
            items: List of items

        Returns:
            Statistics dictionary
        """
        if not items:
            return {
                'total_items': 0,
                'by_category': {},
                'by_source': {},
                'by_reliability': {},
                'avg_relevance_score': 0.0,
            }

        # Count by category
        by_category = defaultdict(int)
        for item in items:
            by_category[item.category.value] += 1

        # Count by source
        by_source = defaultdict(int)
        for item in items:
            by_source[item.source_name] += 1

        # Count by reliability
        by_reliability = defaultdict(int)
        for item in items:
            by_reliability[item.reliability.value] += 1

        # Calculate average relevance
        avg_relevance = sum(item.relevance_score for item in items) / len(items)

        return {
            'total_items': len(items),
            'by_category': dict(by_category),
            'by_source': dict(by_source),
            'by_reliability': dict(by_reliability),
            'avg_relevance_score': round(avg_relevance, 2),
            'timeframe': {
                'oldest': min(items, key=lambda x: x.timestamp).timestamp.isoformat(),
                'newest': max(items, key=lambda x: x.timestamp).timestamp.isoformat(),
            }
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        return self.text_processor.clean_text(text).lower().strip()

    def _compare_reliability(self, item1: InformationItem, item2: InformationItem) -> int:
        """
        Compare reliability of two items.

        Returns:
            1 if item1 more reliable, -1 if item2 more reliable, 0 if equal
        """
        reliability_order = [
            ReliabilityLevel.VERIFIED,
            ReliabilityLevel.HIGH,
            ReliabilityLevel.MEDIUM,
            ReliabilityLevel.LOW,
            ReliabilityLevel.UNVERIFIED,
        ]

        idx1 = reliability_order.index(item1.reliability)
        idx2 = reliability_order.index(item2.reliability)

        if idx1 < idx2:
            return 1
        elif idx1 > idx2:
            return -1
        else:
            return 0

    def _calculate_impact_level(self, item: InformationItem) -> str:
        """Calculate impact level of an item."""
        # High impact: breaking news, high relevance, verified sources
        if (item.category == Category.BREAKING_UPDATES or
            item.relevance_score >= 0.8 or
            item.reliability == ReliabilityLevel.VERIFIED):
            return 'high'

        # Medium impact: medium relevance, recent
        elif item.relevance_score >= 0.5:
            return 'medium'

        # Low impact
        else:
            return 'low'

    def _get_category_priority(self, category: Category) -> float:
        """Get priority score for category."""
        priority_map = {
            Category.BREAKING_UPDATES: 1.0,
            Category.GOVERNANCE: 0.9,
            Category.TRANSPORTATION: 0.8,
            Category.BUSINESS_ECONOMY: 0.7,
            Category.CULTURE_EVENTS: 0.6,
            Category.CITY_LIFE: 0.5,
            Category.FOOD_NIGHTLIFE: 0.4,
            Category.TOURISM: 0.4,
            Category.SOCIAL_MEDIA: 0.3,
            Category.COMMUNITY: 0.5,
        }
        return priority_map.get(category, 0.3)

    def _get_reliability_score(self, reliability: ReliabilityLevel) -> float:
        """Get numeric score for reliability level."""
        score_map = {
            ReliabilityLevel.VERIFIED: 1.0,
            ReliabilityLevel.HIGH: 0.8,
            ReliabilityLevel.MEDIUM: 0.6,
            ReliabilityLevel.LOW: 0.4,
            ReliabilityLevel.UNVERIFIED: 0.2,
        }
        return score_map.get(reliability, 0.5)
