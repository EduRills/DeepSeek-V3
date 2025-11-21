"""Report models for generating intelligence briefs."""

from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from .information_item import InformationItem, Category


class ReportSection(BaseModel):
    """
    A section of the intelligence report.

    Attributes:
        title: Section title
        category: Category this section represents
        items: Information items in this section
        summary: Brief summary of the section
    """
    title: str = Field(..., description="Section title")
    category: Category = Field(..., description="Category")
    items: List[InformationItem] = Field(default_factory=list, description="Information items")
    summary: str = Field(default="", description="Section summary")

    def add_item(self, item: InformationItem):
        """Add an item to the section."""
        self.items.append(item)

    def sort_items_by_relevance(self):
        """Sort items by relevance score (descending)."""
        self.items.sort(key=lambda x: x.relevance_score, reverse=True)

    def sort_items_by_timestamp(self):
        """Sort items by timestamp (most recent first)."""
        self.items.sort(key=lambda x: x.timestamp, reverse=True)

    def get_top_items(self, n: int = 10) -> List[InformationItem]:
        """Get top N items by relevance."""
        self.sort_items_by_relevance()
        return self.items[:n]


class Report(BaseModel):
    """
    Complete intelligence report about Nairobi.

    Attributes:
        title: Report title
        generated_at: When the report was generated
        period_start: Start of the reporting period
        period_end: End of the reporting period
        sections: Report sections organized by category
        metadata: Additional report metadata
        total_items: Total number of items in the report
    """
    title: str = Field(default="Nairobi Intelligence Brief", description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    period_start: datetime = Field(..., description="Period start")
    period_end: datetime = Field(..., description="Period end")
    sections: List[ReportSection] = Field(default_factory=list, description="Report sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Report metadata")
    total_items: int = Field(default=0, description="Total items")

    def add_section(self, section: ReportSection):
        """Add a section to the report."""
        self.sections.append(section)
        self.total_items += len(section.items)

    def get_section_by_category(self, category: Category) -> ReportSection:
        """Get section by category, create if doesn't exist."""
        for section in self.sections:
            if section.category == category:
                return section

        # Create new section if not found
        new_section = ReportSection(
            title=category.value.replace('_', ' ').title(),
            category=category
        )
        self.add_section(new_section)
        return new_section

    def organize_items(self, items: List[InformationItem]):
        """Organize items into appropriate sections."""
        for item in items:
            section = self.get_section_by_category(item.category)
            section.add_item(item)

        # Update total items
        self.total_items = sum(len(section.items) for section in self.sections)

    def sort_all_sections(self):
        """Sort all sections by timestamp."""
        for section in self.sections:
            section.sort_items_by_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.model_dump(mode='json')

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
