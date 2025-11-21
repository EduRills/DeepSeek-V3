from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class Category(str, Enum):
    NEWS = "News"
    EVENTS = "Events"
    TRENDS = "Trends"
    PLACES = "Places"
    ALERTS = "Alerts"
    CULTURE = "Culture"
    ECONOMY = "Economy"
    SOCIAL = "Social Media"
    TRAVEL = "Travel"
    COMMUNITY = "Community"


class Reliability(str, Enum):
    VERIFIED = "verified"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class IntelItem:
    title: str
    summary: str
    source: str
    category: Category
    reliability: Reliability
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_brief_row(self) -> str:
        details = " — ".join(
            [
                self.title,
                self.summary,
                self.metadata.get("location", ""),
                self.source,
            ]
        ).strip(" —")
        return details


@dataclass
class Brief:
    generated_at: datetime
    items: List[IntelItem] = field(default_factory=list)

    def by_category(self, category: Category) -> List[IntelItem]:
        return [item for item in self.items if item.category == category]

    def to_report(self) -> str:
        lines = [f"Nairobi Intelligence Brief — {self.generated_at.isoformat()}"]
        sections = [
            (Category.NEWS, "Breaking Updates"),
            (Category.ALERTS, "City Life & Alerts"),
            (Category.CULTURE, "Culture & Events"),
            (Category.ECONOMY, "Business & Economy"),
            (Category.PLACES, "Food & Nightlife"),
            (Category.SOCIAL, "Social Media Trends"),
            (Category.TRAVEL, "Travel & Movement"),
            (Category.TRENDS, "New Places / Reviews"),
            (Category.COMMUNITY, "Community Stories"),
        ]

        for category, header in sections:
            lines.append("")
            lines.append(header)
            rows = self.by_category(category)
            if not rows:
                lines.append("No updates yet.")
                continue
            for row in rows:
                lines.append(row.to_brief_row())
        lines.append("End of brief.")
        return "\n".join(lines)


@dataclass
class SourceConfig:
    name: str
    url: str
    category: Category
    reliability: Reliability = Reliability.MEDIUM
    headers: Optional[Dict[str, str]] = None
    query: Optional[Dict[str, Any]] = None
    parser: str = "auto"
    auth_token: Optional[str] = None


@dataclass
class AppConfig:
    news_sources: List[SourceConfig]
    social_sources: List[SourceConfig]
    event_sources: List[SourceConfig]
    business_sources: List[SourceConfig]
    travel_sources: List[SourceConfig]
    community_sources: List[SourceConfig]

    def all_sources(self) -> List[SourceConfig]:
        return (
            self.news_sources
            + self.social_sources
            + self.event_sources
            + self.business_sources
            + self.travel_sources
            + self.community_sources
        )
