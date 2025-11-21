"""Web scraper modules for collecting information."""

from .base_scraper import BaseScraper
from .news_scraper import NewsScraper
from .government_scraper import GovernmentScraper
from .tourism_scraper import TourismScraper

__all__ = [
    'BaseScraper',
    'NewsScraper',
    'GovernmentScraper',
    'TourismScraper',
]
