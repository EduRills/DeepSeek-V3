"""Core data model for information items collected about Nairobi."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator


class ReliabilityLevel(str, Enum):
    """Reliability levels for information sources."""
    VERIFIED = "verified"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"


class Category(str, Enum):
    """Categories for information items."""
    BREAKING_UPDATES = "breaking_updates"
    CITY_LIFE = "city_life"
    CULTURE_EVENTS = "culture_events"
    BUSINESS_ECONOMY = "business_economy"
    FOOD_NIGHTLIFE = "food_nightlife"
    TRANSPORTATION = "transportation"
    SOCIAL_MEDIA = "social_media"
    COMMUNITY = "community"
    TOURISM = "tourism"
    GOVERNANCE = "governance"


class InformationItem(BaseModel):
    """
    Model for a single piece of information about Nairobi.

    Attributes:
        id: Unique identifier for the item
        title: Title or headline of the information
        summary: Concise summary of the information
        content: Full content (if available)
        category: Category of the information
        source_name: Name of the source
        source_url: URL of the source
        reliability: Reliability level of the source
        timestamp: When the information was published/created
        collected_at: When the information was collected by our system
        location: Specific location in Nairobi (if applicable)
        tags: Keywords and tags for categorization
        metadata: Additional metadata
        sentiment: Sentiment analysis result (positive, negative, neutral)
        relevance_score: How relevant the information is (0-1)
    """
    id: Optional[str] = Field(default=None, description="Unique identifier")
    title: str = Field(..., description="Title or headline")
    summary: str = Field(..., description="Concise summary")
    content: Optional[str] = Field(default=None, description="Full content")
    category: Category = Field(..., description="Category of information")
    source_name: str = Field(..., description="Name of the source")
    source_url: Optional[HttpUrl] = Field(default=None, description="URL of the source")
    reliability: ReliabilityLevel = Field(..., description="Reliability level")
    timestamp: datetime = Field(..., description="Publication timestamp")
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="Collection timestamp")
    location: Optional[str] = Field(default=None, description="Specific location")
    tags: List[str] = Field(default_factory=list, description="Keywords and tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    sentiment: Optional[str] = Field(default=None, description="Sentiment (positive/negative/neutral)")
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance score")
    impact_level: Optional[str] = Field(default=None, description="Impact level (high/medium/low)")

    @validator('relevance_score')
    def validate_relevance_score(cls, v):
        """Ensure relevance score is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError('Relevance score must be between 0 and 1')
        return v

    @validator('timestamp', 'collected_at', pre=True)
    def parse_datetime(cls, v):
        """Parse datetime strings."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.model_dump(mode='json')

    def is_recent(self, hours: int = 24) -> bool:
        """Check if the item is recent (within specified hours)."""
        age = datetime.utcnow() - self.timestamp
        return age.total_seconds() / 3600 <= hours

    def matches_keywords(self, keywords: List[str]) -> bool:
        """Check if item matches any of the given keywords."""
        text = f"{self.title} {self.summary} {' '.join(self.tags)}".lower()
        return any(keyword.lower() in text for keyword in keywords)
