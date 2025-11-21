"""Government and public services scraper."""

from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import re

from .base_scraper import BaseScraper
from src.models import InformationItem, ReliabilityLevel, Category


class GovernmentScraper(BaseScraper):
    """Scraper for government and public service websites."""

    def __init__(
        self,
        source_name: str,
        base_url: str,
        reliability: ReliabilityLevel = ReliabilityLevel.VERIFIED
    ):
        """Initialize government scraper."""
        super().__init__(source_name, base_url, reliability)

    def scrape(self) -> List[InformationItem]:
        """
        Scrape government announcements and public information.

        Returns:
            List of InformationItem objects
        """
        self.logger.info(f"Starting scrape of {self.source_name}")

        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        items = []

        # Parse based on source
        if "nairobi.go.ke" in self.base_url:
            items = self._scrape_nairobi_county(soup)
        elif "opendata.go.ke" in self.base_url:
            items = self._scrape_open_data(soup)
        else:
            items = self._scrape_generic_gov(soup)

        # Filter relevant items
        items = self.filter_relevant_items(items)

        self.logger.info(f"Scraped {len(items)} government items from {self.source_name}")
        return items

    def _scrape_nairobi_county(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Nairobi City County website."""
        items = []

        # Look for announcements, news, press releases
        announcements = soup.find_all(['div', 'article'], class_=re.compile(r'announcement|news|press'))

        for announcement in announcements[:15]:
            try:
                title_elem = announcement.find(['h1', 'h2', 'h3', 'h4'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                summary_elem = announcement.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                link_elem = announcement.find('a', href=True)
                url = link_elem['href'] if link_elem else None
                if url and not url.startswith('http'):
                    url = f"https://nairobi.go.ke{url}"

                # Government announcements are high priority
                category = self._categorize_government_item(title, summary)

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=url,
                    timestamp=datetime.utcnow(),
                    metadata={'type': 'government_announcement', 'priority': 'high'}
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing announcement: {e}")
                continue

        return items

    def _scrape_open_data(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Kenya Open Data portal."""
        items = []

        # Look for datasets related to Nairobi
        datasets = soup.find_all(['div', 'article'], class_=re.compile(r'dataset|data'))

        for dataset in datasets[:10]:
            try:
                title_elem = dataset.find(['h1', 'h2', 'h3'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Only include if Nairobi-related
                if not self.is_relevant(title):
                    continue

                summary_elem = dataset.find('p', class_=re.compile(r'description|summary'))
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                link_elem = dataset.find('a', href=True)
                url = link_elem['href'] if link_elem else None

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=Category.GOVERNANCE,
                    source_url=url,
                    timestamp=datetime.utcnow(),
                    metadata={'type': 'open_data', 'format': 'dataset'}
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing dataset: {e}")
                continue

        return items

    def _scrape_generic_gov(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Generic government website scraping."""
        items = []

        # Find news/announcements sections
        content_sections = soup.find_all(['article', 'div'], limit=15)

        for section in content_sections:
            try:
                title_elem = section.find(['h1', 'h2', 'h3'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                if len(title) < 10:
                    continue

                summary_elem = section.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else title

                link_elem = section.find('a', href=True)
                url = link_elem['href'] if link_elem else None

                category = self._categorize_government_item(title, summary)

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=url,
                    timestamp=datetime.utcnow()
                )

                items.append(item)

            except Exception as e:
                continue

        return items

    def _categorize_government_item(self, title: str, summary: str) -> Category:
        """Categorize government information."""
        text = f"{title} {summary}".lower()

        # Check for alerts/emergencies
        if any(word in text for word in ['alert', 'emergency', 'urgent', 'warning']):
            return Category.BREAKING_UPDATES

        # Check for transportation/infrastructure
        if any(word in text for word in ['road', 'transport', 'traffic', 'infrastructure']):
            return Category.TRANSPORTATION

        # Default to governance
        return Category.GOVERNANCE
