"""Base collector class for API-based data collection."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models import InformationItem, ReliabilityLevel, Category
from src.utils import get_logger, TextProcessor


class BaseCollector(ABC):
    """
    Abstract base class for all API-based collectors.

    Attributes:
        platform_name: Name of the social media platform
        reliability: Reliability level of the platform
    """

    def __init__(
        self,
        platform_name: str,
        reliability: ReliabilityLevel = ReliabilityLevel.MEDIUM
    ):
        """
        Initialize the collector.

        Args:
            platform_name: Name of the platform
            reliability: Reliability level
        """
        self.platform_name = platform_name
        self.reliability = reliability

        self.logger = get_logger(self.__class__.__name__)
        self.text_processor = TextProcessor()

    @abstractmethod
    def collect(self, query: str = "Nairobi", limit: int = 50) -> List[InformationItem]:
        """
        Main collection method to be implemented by subclasses.

        Args:
            query: Search query
            limit: Maximum number of items to collect

        Returns:
            List of InformationItem objects
        """
        pass

    def create_information_item(
        self,
        title: str,
        summary: str,
        category: Category = Category.SOCIAL_MEDIA,
        source_url: Optional[str] = None,
        content: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InformationItem:
        """
        Create an InformationItem from collected data.

        Args:
            title: Title of the information
            summary: Summary text
            category: Category
            source_url: URL of the source
            content: Full content
            timestamp: Publication timestamp
            location: Specific location
            tags: Tags and keywords
            metadata: Additional metadata

        Returns:
            InformationItem instance
        """
        # Clean text
        title = self.text_processor.clean_text(title)
        summary = self.text_processor.clean_text(summary)

        # Calculate relevance score
        full_text = f"{title} {summary}"
        relevance_score = self.text_processor.calculate_relevance_score(full_text)

        # Analyze sentiment
        sentiment = self.text_processor.analyze_sentiment(summary)

        # Extract keywords and hashtags
        if tags is None:
            tags = self.text_processor.extract_keywords(full_text)
            hashtags = self.text_processor.extract_hashtags(f"{title} {summary}")
            tags.extend(hashtags)

        # Use current time if timestamp not provided
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Add platform to metadata
        if metadata is None:
            metadata = {}
        metadata['platform'] = self.platform_name

        return InformationItem(
            title=title,
            summary=summary,
            content=content,
            category=category,
            source_name=self.platform_name,
            source_url=source_url,
            reliability=self.reliability,
            timestamp=timestamp,
            location=location,
            tags=tags,
            metadata=metadata,
            sentiment=sentiment,
            relevance_score=relevance_score
        )

    def filter_relevant_items(
        self,
        items: List[InformationItem],
        min_relevance: float = 0.3
    ) -> List[InformationItem]:
        """
        Filter items to only include those relevant to Nairobi.

        Args:
            items: List of items to filter
            min_relevance: Minimum relevance score

        Returns:
            Filtered list of items
        """
        return [item for item in items if item.relevance_score >= min_relevance]

    def deduplicate_items(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Remove duplicate items based on title similarity.

        Args:
            items: List of items

        Returns:
            Deduplicated list
        """
        seen_titles = set()
        unique_items = []

        for item in items:
            title_lower = item.title.lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_items.append(item)

        return unique_items
