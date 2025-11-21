"""Base scraper class for all web scrapers."""

import time
import requests
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from src.models import InformationItem, ReliabilityLevel, Category
from src.utils import get_logger, TextProcessor


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.

    Attributes:
        source_name: Name of the information source
        base_url: Base URL of the source
        reliability: Reliability level of the source
        timeout: Request timeout in seconds
        retry_count: Number of retries for failed requests
        rate_limit_delay: Delay between requests in seconds
    """

    def __init__(
        self,
        source_name: str,
        base_url: str,
        reliability: ReliabilityLevel = ReliabilityLevel.MEDIUM,
        timeout: int = 30,
        retry_count: int = 3,
        rate_limit_delay: float = 2.0
    ):
        """
        Initialize the scraper.

        Args:
            source_name: Name of the source
            base_url: Base URL of the source
            reliability: Reliability level
            timeout: Request timeout
            retry_count: Number of retries
            rate_limit_delay: Delay between requests
        """
        self.source_name = source_name
        self.base_url = base_url
        self.reliability = reliability
        self.timeout = timeout
        self.retry_count = retry_count
        self.rate_limit_delay = rate_limit_delay

        self.logger = get_logger(self.__class__.__name__)
        self.text_processor = TextProcessor()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with headers."""
        session = requests.Session()
        ua = UserAgent()

        session.headers.update({
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        return session

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return BeautifulSoup object.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(self.retry_count):
            try:
                self.logger.info(f"Fetching: {url} (attempt {attempt + 1}/{self.retry_count})")

                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()

                # Apply rate limiting
                time.sleep(self.rate_limit_delay)

                return BeautifulSoup(response.content, 'lxml')

            except requests.RequestException as e:
                self.logger.warning(f"Error fetching {url}: {e}")

                if attempt < self.retry_count - 1:
                    wait_time = (attempt + 1) * 2
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to fetch {url} after {self.retry_count} attempts")
                    return None

        return None

    def create_information_item(
        self,
        title: str,
        summary: str,
        category: Category,
        source_url: Optional[str] = None,
        content: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InformationItem:
        """
        Create an InformationItem from scraped data.

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

        # Extract keywords if tags not provided
        if tags is None:
            tags = self.text_processor.extract_keywords(full_text)

        # Use current time if timestamp not provided
        if timestamp is None:
            timestamp = datetime.utcnow()

        return InformationItem(
            title=title,
            summary=summary,
            content=content,
            category=category,
            source_name=self.source_name,
            source_url=source_url,
            reliability=self.reliability,
            timestamp=timestamp,
            location=location,
            tags=tags,
            metadata=metadata or {},
            sentiment=sentiment,
            relevance_score=relevance_score
        )

    @abstractmethod
    def scrape(self) -> List[InformationItem]:
        """
        Main scraping method to be implemented by subclasses.

        Returns:
            List of InformationItem objects
        """
        pass

    def is_relevant(self, text: str) -> bool:
        """
        Check if content is relevant to Nairobi.

        Args:
            text: Text to check

        Returns:
            True if relevant
        """
        return self.text_processor.is_nairobi_related(text)

    def filter_relevant_items(self, items: List[InformationItem]) -> List[InformationItem]:
        """
        Filter items to only include those relevant to Nairobi.

        Args:
            items: List of items to filter

        Returns:
            Filtered list of items
        """
        return [item for item in items if item.relevance_score >= 0.3]
