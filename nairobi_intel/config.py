from __future__ import annotations

from typing import List

from .models import AppConfig, Category, Reliability, SourceConfig


NEWS_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="Nation Africa",
        url="https://nation.africa/rss",
        category=Category.NEWS,
        reliability=Reliability.HIGH,
        parser="rss",
    ),
    SourceConfig(
        name="BBC Africa",
        url="https://feeds.bbci.co.uk/news/world/africa/rss.xml",
        category=Category.NEWS,
        reliability=Reliability.VERIFIED,
        parser="rss",
    ),
    SourceConfig(
        name="Business Daily Africa",
        url="https://www.businessdailyafrica.com/feeds/home.rdf",
        category=Category.ECONOMY,
        reliability=Reliability.HIGH,
        parser="rss",
    ),
]

SOCIAL_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="Twitter Nairobi Trends",
        url="https://api.twitter.com/2/tweets/search/recent",
        category=Category.SOCIAL,
        parser="twitter_recent",
        query={"query": "Nairobi", "max_results": 20},
        reliability=Reliability.MEDIUM,
    ),
    SourceConfig(
        name="YouTube Nairobi Travel",
        url="https://www.googleapis.com/youtube/v3/search",
        category=Category.SOCIAL,
        parser="youtube_search",
        query={"q": "Nairobi travel vlog", "maxResults": 10},
        reliability=Reliability.MEDIUM,
    ),
]

EVENT_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="Kenya Tourism Board",
        url="https://www.magicalkenya.com/feed/",
        category=Category.CULTURE,
        parser="rss",
        reliability=Reliability.HIGH,
    ),
    SourceConfig(
        name="Ticket Sasa",
        url="https://www.ticketsasa.com/events",
        category=Category.EVENTS,
        parser="html_events",
    ),
]

BUSINESS_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="TechCabal Kenya",
        url="https://techcabal.com/feed",
        category=Category.ECONOMY,
        parser="rss",
        reliability=Reliability.HIGH,
    ),
    SourceConfig(
        name="CIO Africa",
        url="https://cioafrica.co/feed/",
        category=Category.ECONOMY,
        parser="rss",
    ),
]

TRAVEL_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="Kenya Civil Aviation Authority",
        url="https://www.kcaa.or.ke/",
        category=Category.TRAVEL,
        parser="html_bulletins",
        reliability=Reliability.VERIFIED,
    ),
    SourceConfig(
        name="NTSA Traffic Alerts",
        url="https://ntsa.go.ke/",
        category=Category.ALERTS,
        parser="html_bulletins",
        reliability=Reliability.HIGH,
    ),
]

COMMUNITY_SOURCES: List[SourceConfig] = [
    SourceConfig(
        name="Kenya Open Data",
        url="https://www.opendata.go.ke/browse?limitTo=datasets",
        category=Category.COMMUNITY,
        parser="html_bulletins",
        reliability=Reliability.VERIFIED,
    ),
]


def default_app_config() -> AppConfig:
    return AppConfig(
        news_sources=NEWS_SOURCES,
        social_sources=SOCIAL_SOURCES,
        event_sources=EVENT_SOURCES,
        business_sources=BUSINESS_SOURCES,
        travel_sources=TRAVEL_SOURCES,
        community_sources=COMMUNITY_SOURCES,
    )
