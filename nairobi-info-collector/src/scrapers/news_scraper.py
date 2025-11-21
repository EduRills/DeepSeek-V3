"""News scraper for collecting news articles about Nairobi."""

from typing import List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

from .base_scraper import BaseScraper
from src.models import InformationItem, ReliabilityLevel, Category


class NewsScraper(BaseScraper):
    """Scraper for news websites."""

    def __init__(
        self,
        source_name: str,
        base_url: str,
        reliability: ReliabilityLevel = ReliabilityLevel.HIGH
    ):
        """Initialize news scraper."""
        super().__init__(source_name, base_url, reliability)

    def scrape(self) -> List[InformationItem]:
        """
        Scrape news articles.

        Returns:
            List of InformationItem objects
        """
        self.logger.info(f"Starting scrape of {self.source_name}")

        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        items = []

        # Different parsing strategies based on source
        if "nation.africa" in self.base_url:
            items = self._scrape_nation_africa(soup)
        elif "standardmedia.co.ke" in self.base_url:
            items = self._scrape_standard_media(soup)
        elif "citizen.digital" in self.base_url:
            items = self._scrape_citizen_digital(soup)
        elif "businessdailyafrica.com" in self.base_url:
            items = self._scrape_business_daily(soup)
        else:
            # Generic scraping
            items = self._scrape_generic(soup)

        # Filter relevant items
        items = self.filter_relevant_items(items)

        self.logger.info(f"Scraped {len(items)} items from {self.source_name}")
        return items

    def _scrape_nation_africa(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Nation Africa website."""
        items = []

        # Find article containers (adjust selectors based on actual site structure)
        articles = soup.find_all('article', class_=re.compile(r'story|article|post'))

        for article in articles[:20]:  # Limit to 20 articles
            try:
                # Extract title
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|headline'))
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Extract summary/description
                summary_elem = article.find(['p', 'div'], class_=re.compile(r'summary|excerpt|description'))
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                # Extract link
                link_elem = article.find('a', href=True)
                article_url = link_elem['href'] if link_elem else None
                if article_url and not article_url.startswith('http'):
                    article_url = f"https://nation.africa{article_url}"

                # Extract timestamp
                time_elem = article.find('time', datetime=True)
                timestamp = self._parse_timestamp(time_elem['datetime']) if time_elem else datetime.utcnow()

                # Determine category
                category = self._determine_category(title, summary)

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=article_url,
                    timestamp=timestamp
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing article: {e}")
                continue

        return items

    def _scrape_standard_media(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Standard Media website."""
        items = []

        articles = soup.find_all(['article', 'div'], class_=re.compile(r'article|story|post'))

        for article in articles[:20]:
            try:
                title_elem = article.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'title|headline'))
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                summary_elem = article.find('p', class_=re.compile(r'excerpt|summary|intro'))
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                link_elem = article.find('a', href=True)
                article_url = link_elem['href'] if link_elem else None
                if article_url and not article_url.startswith('http'):
                    article_url = f"https://www.standardmedia.co.ke{article_url}"

                category = self._determine_category(title, summary)

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=article_url,
                    timestamp=datetime.utcnow()
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing article: {e}")
                continue

        return items

    def _scrape_citizen_digital(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Citizen Digital website."""
        return self._scrape_generic(soup)

    def _scrape_business_daily(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Business Daily website."""
        items = []

        articles = soup.find_all(['article', 'div'], class_=re.compile(r'article|story'))

        for article in articles[:20]:
            try:
                title_elem = article.find(['h1', 'h2', 'h3'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                summary_elem = article.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                link_elem = article.find('a', href=True)
                article_url = link_elem['href'] if link_elem else None

                # Business news typically falls under BUSINESS_ECONOMY
                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=Category.BUSINESS_ECONOMY,
                    source_url=article_url,
                    timestamp=datetime.utcnow()
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing article: {e}")
                continue

        return items

    def _scrape_generic(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Generic scraping method for unknown news sites."""
        items = []

        # Try to find articles using common patterns
        articles = soup.find_all(['article', 'div'], limit=20)

        for article in articles:
            try:
                # Find title
                title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if len(title) < 10:  # Skip very short titles
                    continue

                # Find summary
                summary_elem = article.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                # Find link
                link_elem = article.find('a', href=True)
                article_url = link_elem['href'] if link_elem else None

                category = self._determine_category(title, summary)

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=article_url,
                    timestamp=datetime.utcnow()
                )

                items.append(item)

            except Exception as e:
                continue

        return items

    def _determine_category(self, title: str, summary: str) -> Category:
        """
        Determine the category of a news article based on content.

        Args:
            title: Article title
            summary: Article summary

        Returns:
            Category
        """
        text = f"{title} {summary}".lower()

        # Check for breaking/urgent news
        if any(word in text for word in ['breaking', 'urgent', 'alert', 'emergency']):
            return Category.BREAKING_UPDATES

        # Check for business/economy
        if any(word in text for word in ['business', 'economy', 'startup', 'investment', 'funding', 'tech']):
            return Category.BUSINESS_ECONOMY

        # Check for culture/events
        if any(word in text for word in ['concert', 'festival', 'exhibition', 'museum', 'art', 'music']):
            return Category.CULTURE_EVENTS

        # Check for transportation
        if any(word in text for word in ['traffic', 'road', 'transport', 'matatu', 'airport']):
            return Category.TRANSPORTATION

        # Check for governance
        if any(word in text for word in ['government', 'county', 'governor', 'policy', 'parliament']):
            return Category.GOVERNANCE

        # Check for food/nightlife
        if any(word in text for word in ['restaurant', 'food', 'dining', 'bar', 'club', 'nightlife']):
            return Category.FOOD_NIGHTLIFE

        # Default to city life
        return Category.CITY_LIFE

    def _parse_timestamp(self, datetime_str: str) -> datetime:
        """
        Parse timestamp from various formats.

        Args:
            datetime_str: Datetime string

        Returns:
            Parsed datetime
        """
        try:
            # Try ISO format
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except Exception:
            # Return current time if parsing fails
            return datetime.utcnow()
