from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Iterable, List

from .config import default_app_config
from .models import AppConfig, Brief, Category, IntelItem
from .sources import fetch_stubbed_items, gather_from_sources


class IntelCollector:
    """Coordinates multi-source collection into a structured brief."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or default_app_config()

    async def collect(self, include_stub: bool = False, skip_network: bool = False) -> Brief:
        items: List[IntelItem] = []
        if not skip_network:
            fetched = await gather_from_sources(self.config.all_sources())
            items.extend(fetched)
        if include_stub:
            items.extend(await fetch_stubbed_items())
        items = self._deduplicate(items)
        return Brief(generated_at=datetime.now(timezone.utc), items=items)

    def _deduplicate(self, items: Iterable[IntelItem]) -> List[IntelItem]:
        seen = set()
        unique: List[IntelItem] = []
        for item in items:
            key = (item.title.strip().lower(), item.source)
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    async def collect_by_category(
        self, category: Category, include_stub: bool = False, skip_network: bool = False
    ) -> Brief:
        filtered_config = AppConfig(
            news_sources=[s for s in self.config.news_sources if s.category == category],
            social_sources=[s for s in self.config.social_sources if s.category == category],
            event_sources=[s for s in self.config.event_sources if s.category == category],
            business_sources=[s for s in self.config.business_sources if s.category == category],
            travel_sources=[s for s in self.config.travel_sources if s.category == category],
            community_sources=[s for s in self.config.community_sources if s.category == category],
        )
        collector = IntelCollector(filtered_config)
        return await collector.collect(include_stub=include_stub, skip_network=skip_network)


async def demo() -> None:
    collector = IntelCollector()
    brief = await collector.collect(include_stub=True, skip_network=True)
    print(brief.to_report())


if __name__ == "__main__":
    asyncio.run(demo())
