from __future__ import annotations

import asyncio
import json
from typing import Iterable, List

import httpx
from bs4 import BeautifulSoup
import feedparser

from .models import Category, IntelItem, Reliability, SourceConfig


class SourceClient:
    def __init__(self, config: SourceConfig, timeout: float = 10.0) -> None:
        self.config = config
        self.timeout = timeout

    async def fetch(self) -> List[IntelItem]:
        if self.config.parser == "rss":
            return await self._fetch_rss()
        if self.config.parser == "twitter_recent":
            return await self._fetch_twitter()
        if self.config.parser == "youtube_search":
            return await self._fetch_youtube()
        if self.config.parser == "html_events":
            return await self._fetch_html_events()
        return await self._fetch_html_bulletins()

    async def _fetch_rss(self) -> List[IntelItem]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.config.url, headers=self.config.headers)
            response.raise_for_status()
        feed = feedparser.parse(response.text)
        items: List[IntelItem] = []
        for entry in feed.entries[:20]:
            items.append(
                IntelItem(
                    title=entry.get("title", ""),
                    summary=entry.get("summary", ""),
                    source=self.config.name,
                    category=self.config.category,
                    reliability=self.config.reliability,
                    metadata={
                        "link": entry.get("link"),
                        "published": entry.get("published"),
                    },
                )
            )
        return items

    async def _fetch_twitter(self) -> List[IntelItem]:
        headers = self.config.headers or {}
        if self.config.auth_token:
            headers = {**headers, "Authorization": f"Bearer {self.config.auth_token}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.config.url, headers=headers, params=self.config.query)
            response.raise_for_status()
        payload = response.json()
        tweets = payload.get("data", [])
        return [
            IntelItem(
                title=tweet.get("text", ""),
                summary="Recent Nairobi discussion on X",
                source=self.config.name,
                category=self.config.category,
                reliability=self.config.reliability,
                metadata={"id": tweet.get("id"), "raw": json.dumps(tweet)[:500]},
            )
            for tweet in tweets
        ]

    async def _fetch_youtube(self) -> List[IntelItem]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.config.url, params=self.config.query, headers=self.config.headers)
            response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        return [
            IntelItem(
                title=item.get("snippet", {}).get("title", ""),
                summary=item.get("snippet", {}).get("description", ""),
                source=self.config.name,
                category=self.config.category,
                reliability=self.config.reliability,
                metadata={
                    "channel": item.get("snippet", {}).get("channelTitle"),
                    "published": item.get("snippet", {}).get("publishedAt"),
                },
            )
            for item in items
        ]

    async def _fetch_html_events(self) -> List[IntelItem]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.config.url, headers=self.config.headers)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select(".event, .card, article")
        items: List[IntelItem] = []
        for card in cards[:20]:
            title = card.get_text(strip=True)[:160]
            items.append(
                IntelItem(
                    title=title or "Nairobi event",
                    summary="Upcoming event listing",
                    source=self.config.name,
                    category=self.config.category,
                    reliability=self.config.reliability,
                )
            )
        return items

    async def _fetch_html_bulletins(self) -> List[IntelItem]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.config.url, headers=self.config.headers)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items: List[IntelItem] = []
        for link in soup.find_all("a")[:30]:
            label = link.get_text(strip=True)
            if not label:
                continue
            items.append(
                IntelItem(
                    title=label[:120],
                    summary="Public service or travel bulletin",
                    source=self.config.name,
                    category=self.config.category,
                    reliability=self.config.reliability,
                    metadata={"href": link.get("href")},
                )
            )
        return items


async def gather_from_sources(configs: Iterable[SourceConfig]) -> List[IntelItem]:
    tasks = [SourceClient(cfg).fetch() for cfg in configs]
    results: List[IntelItem] = []
    for batch in await asyncio.gather(*tasks):
        results.extend(batch)
    return results


async def fetch_stubbed_items() -> List[IntelItem]:
    return [
        IntelItem(
            title="Stub: Traffic moving smoothly on Nairobi Expressway",
            summary="No major incidents reported",
            source="Local Monitor",
            category=Category.ALERTS,
            reliability=Reliability.MEDIUM,
            metadata={"location": "Nairobi Expressway"},
        ),
        IntelItem(
            title="Stub: Weekend music festival at Ngong Racecourse",
            summary="Headliners announced for Saturday",
            source="Events Desk",
            category=Category.CULTURE,
            reliability=Reliability.MEDIUM,
            metadata={"location": "Ngong Racecourse"},
        ),
    ]
