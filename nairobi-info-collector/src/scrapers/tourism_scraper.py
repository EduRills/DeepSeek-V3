"""Tourism and hospitality information scraper."""

from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
import re

from .base_scraper import BaseScraper
from src.models import InformationItem, ReliabilityLevel, Category


class TourismScraper(BaseScraper):
    """Scraper for tourism and hospitality websites."""

    def __init__(
        self,
        source_name: str,
        base_url: str,
        reliability: ReliabilityLevel = ReliabilityLevel.MEDIUM
    ):
        """Initialize tourism scraper."""
        super().__init__(source_name, base_url, reliability)

    def scrape(self) -> List[InformationItem]:
        """
        Scrape tourism information.

        Returns:
            List of InformationItem objects
        """
        self.logger.info(f"Starting scrape of {self.source_name}")

        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        items = []

        # Parse based on source
        if "tripadvisor.com" in self.base_url:
            items = self._scrape_tripadvisor(soup)
        elif "lonelyplanet.com" in self.base_url:
            items = self._scrape_lonely_planet(soup)
        else:
            items = self._scrape_generic_tourism(soup)

        # Filter relevant items
        items = self.filter_relevant_items(items)

        self.logger.info(f"Scraped {len(items)} tourism items from {self.source_name}")
        return items

    def _scrape_tripadvisor(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape TripAdvisor content."""
        items = []

        # Look for attractions, restaurants, hotels
        listings = soup.find_all(['div', 'article'], class_=re.compile(r'listing|attraction|restaurant'))

        for listing in listings[:15]:
            try:
                title_elem = listing.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'title|name'))
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Extract rating if available
                rating_elem = listing.find(class_=re.compile(r'rating|stars'))
                rating = rating_elem.get_text(strip=True) if rating_elem else None

                # Extract review snippet
                review_elem = listing.find(['p', 'div'], class_=re.compile(r'review|description'))
                summary = review_elem.get_text(strip=True) if review_elem else title

                link_elem = listing.find('a', href=True)
                url = link_elem['href'] if link_elem else None
                if url and not url.startswith('http'):
                    url = f"https://www.tripadvisor.com{url}"

                # Determine category
                category = self._categorize_tourism_item(title, summary)

                metadata = {'platform': 'tripadvisor'}
                if rating:
                    metadata['rating'] = rating

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=url,
                    timestamp=datetime.utcnow(),
                    metadata=metadata
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing listing: {e}")
                continue

        return items

    def _scrape_lonely_planet(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Scrape Lonely Planet content."""
        items = []

        # Look for attractions and places
        places = soup.find_all(['div', 'article'], class_=re.compile(r'place|attraction|poi'))

        for place in places[:15]:
            try:
                title_elem = place.find(['h1', 'h2', 'h3'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                desc_elem = place.find('p', class_=re.compile(r'description|summary|intro'))
                summary = desc_elem.get_text(strip=True) if desc_elem else title

                link_elem = place.find('a', href=True)
                url = link_elem['href'] if link_elem else None
                if url and not url.startswith('http'):
                    url = f"https://www.lonelyplanet.com{url}"

                category = self._categorize_tourism_item(title, summary)

                item = self.create_information_item(
                    title=title,
                    summary=summary,
                    category=category,
                    source_url=url,
                    timestamp=datetime.utcnow(),
                    metadata={'platform': 'lonely_planet'}
                )

                items.append(item)

            except Exception as e:
                self.logger.warning(f"Error parsing place: {e}")
                continue

        return items

    def _scrape_generic_tourism(self, soup: BeautifulSoup) -> List[InformationItem]:
        """Generic tourism website scraping."""
        items = []

        sections = soup.find_all(['article', 'div'], limit=15)

        for section in sections:
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

                category = self._categorize_tourism_item(title, summary)

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

    def _categorize_tourism_item(self, title: str, summary: str) -> Category:
        """Categorize tourism information."""
        text = f"{title} {summary}".lower()

        # Check for food/dining
        if any(word in text for word in ['restaurant', 'food', 'dining', 'cafe', 'bar', 'nightlife']):
            return Category.FOOD_NIGHTLIFE

        # Check for events/culture
        if any(word in text for word in ['museum', 'gallery', 'theater', 'concert', 'festival']):
            return Category.CULTURE_EVENTS

        # Default to tourism
        return Category.TOURISM
