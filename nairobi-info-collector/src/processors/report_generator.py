"""Report generator for creating formatted intelligence briefs."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.models import Report, ReportSection, InformationItem, Category
from src.utils import get_logger


class ReportGenerator:
    """
    Generate formatted reports from collected information.

    Supports multiple output formats:
    - JSON
    - Markdown
    - HTML
    """

    def __init__(self, output_dir: str = "data"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory for saving reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger(self.__class__.__name__)

    def generate_report(
        self,
        items: List[InformationItem],
        period_start: datetime,
        period_end: Optional[datetime] = None,
        title: str = "Nairobi Intelligence Brief"
    ) -> Report:
        """
        Generate a report from information items.

        Args:
            items: List of information items
            period_start: Start of reporting period
            period_end: End of reporting period (default: now)
            title: Report title

        Returns:
            Report object
        """
        if period_end is None:
            period_end = datetime.utcnow()

        self.logger.info(f"Generating report with {len(items)} items")

        # Create report
        report = Report(
            title=title,
            period_start=period_start,
            period_end=period_end
        )

        # Organize items into sections by category
        report.organize_items(items)

        # Sort all sections
        report.sort_all_sections()

        # Add metadata
        report.metadata = {
            'generated_at': datetime.utcnow().isoformat(),
            'item_count': len(items),
            'categories': len(report.sections),
        }

        self.logger.info(f"Report generated with {len(report.sections)} sections")
        return report

    def save_as_json(self, report: Report, filename: Optional[str] = None) -> str:
        """
        Save report as JSON file.

        Args:
            report: Report to save
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"nairobi_report_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        self.logger.info(f"Report saved as JSON: {filepath}")
        return str(filepath)

    def save_as_markdown(self, report: Report, filename: Optional[str] = None) -> str:
        """
        Save report as Markdown file.

        Args:
            report: Report to save
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"nairobi_report_{timestamp}.md"

        filepath = self.output_dir / filename

        markdown = self._generate_markdown(report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        self.logger.info(f"Report saved as Markdown: {filepath}")
        return str(filepath)

    def save_as_html(self, report: Report, filename: Optional[str] = None) -> str:
        """
        Save report as HTML file.

        Args:
            report: Report to save
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"nairobi_report_{timestamp}.html"

        filepath = self.output_dir / filename

        html = self._generate_html(report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        self.logger.info(f"Report saved as HTML: {filepath}")
        return str(filepath)

    def _generate_markdown(self, report: Report) -> str:
        """Generate Markdown formatted report."""
        md = []

        # Header
        md.append(f"# {report.title}\n")
        md.append(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        md.append(f"**Period:** {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}\n")
        md.append(f"**Total Items:** {report.total_items}\n")
        md.append("\n---\n\n")

        # Sections
        for section in report.sections:
            if not section.items:
                continue

            md.append(f"## {section.title}\n\n")

            for item in section.items[:20]:  # Limit to top 20 items per section
                md.append(f"### {item.title}\n\n")
                md.append(f"**Summary:** {item.summary}\n\n")

                # Metadata
                md.append(f"- **Source:** {item.source_name}")
                if item.source_url:
                    md.append(f" ([Link]({item.source_url}))")
                md.append("\n")

                md.append(f"- **Published:** {item.timestamp.strftime('%Y-%m-%d %H:%M')}\n")
                md.append(f"- **Reliability:** {item.reliability.value.title()}\n")
                md.append(f"- **Relevance Score:** {item.relevance_score:.2f}\n")

                if item.sentiment:
                    md.append(f"- **Sentiment:** {item.sentiment.title()}\n")

                if item.location:
                    md.append(f"- **Location:** {item.location}\n")

                if item.tags:
                    md.append(f"- **Tags:** {', '.join(item.tags[:10])}\n")

                md.append("\n---\n\n")

        # Footer
        md.append("\n## End of Brief\n")

        return ''.join(md)

    def _generate_html(self, report: Report) -> str:
        """Generate HTML formatted report."""
        html = []

        # HTML header
        html.append("<!DOCTYPE html>\n")
        html.append("<html lang='en'>\n")
        html.append("<head>\n")
        html.append("  <meta charset='UTF-8'>\n")
        html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        html.append(f"  <title>{report.title}</title>\n")
        html.append("  <style>\n")
        html.append(self._get_html_styles())
        html.append("  </style>\n")
        html.append("</head>\n")
        html.append("<body>\n")

        # Report header
        html.append(f"  <div class='container'>\n")
        html.append(f"    <h1>{report.title}</h1>\n")
        html.append(f"    <div class='report-meta'>\n")
        html.append(f"      <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>\n")
        html.append(f"      <p><strong>Period:</strong> {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}</p>\n")
        html.append(f"      <p><strong>Total Items:</strong> {report.total_items}</p>\n")
        html.append(f"    </div>\n")

        # Sections
        for section in report.sections:
            if not section.items:
                continue

            html.append(f"    <div class='section'>\n")
            html.append(f"      <h2>{section.title}</h2>\n")

            for item in section.items[:20]:
                # Determine item class based on impact
                impact_class = item.impact_level or 'medium'

                html.append(f"      <div class='item item-{impact_class}'>\n")
                html.append(f"        <h3>{item.title}</h3>\n")
                html.append(f"        <p class='summary'>{item.summary}</p>\n")

                # Metadata
                html.append(f"        <div class='metadata'>\n")
                html.append(f"          <span class='source'><strong>Source:</strong> {item.source_name}</span>\n")
                html.append(f"          <span class='timestamp'><strong>Published:</strong> {item.timestamp.strftime('%Y-%m-%d %H:%M')}</span>\n")
                html.append(f"          <span class='reliability reliability-{item.reliability.value}'>{item.reliability.value.title()}</span>\n")

                if item.sentiment:
                    html.append(f"          <span class='sentiment sentiment-{item.sentiment}'>{item.sentiment.title()}</span>\n")

                html.append(f"        </div>\n")

                if item.source_url:
                    html.append(f"        <p class='link'><a href='{item.source_url}' target='_blank'>View Source →</a></p>\n")

                if item.tags:
                    html.append(f"        <div class='tags'>\n")
                    for tag in item.tags[:10]:
                        html.append(f"          <span class='tag'>{tag}</span>\n")
                    html.append(f"        </div>\n")

                html.append(f"      </div>\n")

            html.append(f"    </div>\n")

        html.append(f"  </div>\n")
        html.append("</body>\n")
        html.append("</html>\n")

        return ''.join(html)

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML report."""
        return """
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f5f5;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 {
      color: #2c3e50;
      border-bottom: 3px solid #3498db;
      padding-bottom: 10px;
    }
    h2 {
      color: #34495e;
      margin-top: 30px;
      border-left: 4px solid #3498db;
      padding-left: 15px;
    }
    .report-meta {
      background: #ecf0f1;
      padding: 15px;
      border-radius: 5px;
      margin: 20px 0;
    }
    .report-meta p {
      margin: 5px 0;
    }
    .section {
      margin: 30px 0;
    }
    .item {
      background: #fff;
      border: 1px solid #e0e0e0;
      border-left: 4px solid #95a5a6;
      padding: 20px;
      margin: 15px 0;
      border-radius: 5px;
      transition: all 0.3s;
    }
    .item:hover {
      box-shadow: 0 3px 15px rgba(0,0,0,0.1);
    }
    .item-high {
      border-left-color: #e74c3c;
    }
    .item-medium {
      border-left-color: #f39c12;
    }
    .item-low {
      border-left-color: #95a5a6;
    }
    .item h3 {
      margin: 0 0 10px 0;
      color: #2c3e50;
    }
    .summary {
      color: #555;
      line-height: 1.7;
    }
    .metadata {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      margin: 15px 0;
      font-size: 0.9em;
    }
    .metadata span {
      background: #ecf0f1;
      padding: 5px 10px;
      border-radius: 3px;
    }
    .reliability-verified {
      background: #2ecc71 !important;
      color: white;
    }
    .reliability-high {
      background: #3498db !important;
      color: white;
    }
    .reliability-medium {
      background: #f39c12 !important;
      color: white;
    }
    .sentiment-positive {
      background: #2ecc71 !important;
      color: white;
    }
    .sentiment-negative {
      background: #e74c3c !important;
      color: white;
    }
    .link a {
      color: #3498db;
      text-decoration: none;
      font-weight: 500;
    }
    .link a:hover {
      text-decoration: underline;
    }
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }
    .tag {
      background: #3498db;
      color: white;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 0.85em;
    }
        """

    def print_summary(self, report: Report):
        """Print a console summary of the report."""
        print(f"\n{'='*80}")
        print(f"{report.title}")
        print(f"{'='*80}")
        print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}")
        print(f"Total Items: {report.total_items}")
        print(f"{'='*80}\n")

        for section in report.sections:
            if not section.items:
                continue

            print(f"\n## {section.title.upper()} ({len(section.items)} items)")
            print(f"{'-'*80}")

            for i, item in enumerate(section.items[:5], 1):  # Show top 5
                print(f"\n{i}. {item.title}")
                print(f"   {item.summary[:100]}...")
                print(f"   Source: {item.source_name} | {item.timestamp.strftime('%Y-%m-%d %H:%M')}")

        print(f"\n{'='*80}")
        print("End of Brief")
        print(f"{'='*80}\n")
