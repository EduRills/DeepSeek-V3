#!/usr/bin/env python3
"""
Example usage of the Nairobi Information Collector

This script demonstrates various ways to use the collector programmatically.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from src.orchestrator import NairobiInfoOrchestrator
from src.scrapers import NewsScraper
from src.collectors import TwitterCollector
from src.processors import DataProcessor, ReportGenerator
from src.models import Category


def example_1_basic_collection():
    """Example 1: Basic single collection run."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Collection")
    print("="*80 + "\n")

    # Initialize orchestrator
    orchestrator = NairobiInfoOrchestrator()

    # Run single collection
    result = orchestrator.run_collection_cycle(
        output_formats=['json', 'markdown']
    )

    print(f"\nCollected {result['items_collected']} items")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Output files: {result['output_files']}")


def example_2_single_source():
    """Example 2: Collect from a single news source."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Single Source Collection")
    print("="*80 + "\n")

    # Create a single scraper
    scraper = NewsScraper(
        source_name="Nation Africa",
        base_url="https://nation.africa/kenya/nairobi"
    )

    # Collect items
    items = scraper.scrape()

    print(f"Collected {len(items)} items from Nation Africa")

    # Display first few items
    for i, item in enumerate(items[:3], 1):
        print(f"\n{i}. {item.title}")
        print(f"   Category: {item.category.value}")
        print(f"   Relevance: {item.relevance_score:.2f}")


def example_3_filter_by_category():
    """Example 3: Filter items by specific category."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Filter by Category")
    print("="*80 + "\n")

    orchestrator = NairobiInfoOrchestrator()

    # Collect all items
    all_items = orchestrator.collect_all(parallel=True)

    # Filter by category
    business_items = [
        item for item in all_items
        if item.category == Category.BUSINESS_ECONOMY
    ]

    print(f"Total items: {len(all_items)}")
    print(f"Business & Economy items: {len(business_items)}")

    # Display business items
    for i, item in enumerate(business_items[:5], 1):
        print(f"\n{i}. {item.title}")
        print(f"   Source: {item.source_name}")
        print(f"   Published: {item.timestamp}")


def example_4_custom_processing():
    """Example 4: Custom data processing."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Processing")
    print("="*80 + "\n")

    orchestrator = NairobiInfoOrchestrator()

    # Collect items
    items = orchestrator.collect_all(parallel=True)

    # Create custom processor with different settings
    processor = DataProcessor(
        min_relevance_score=0.5,  # Higher threshold
        max_age_hours=24          # Only last 24 hours
    )

    # Process items
    processed_items = processor.process(items)

    # Get statistics
    stats = processor.get_statistics(processed_items)

    print(f"Original items: {len(items)}")
    print(f"After processing: {len(processed_items)}")
    print(f"\nStatistics:")
    print(f"  Average relevance: {stats['avg_relevance_score']}")
    print(f"  By category: {stats['by_category']}")
    print(f"  By source: {stats['by_source']}")


def example_5_twitter_only():
    """Example 5: Collect only from Twitter."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Twitter Collection Only")
    print("="*80 + "\n")

    # Create Twitter collector
    twitter = TwitterCollector()

    # Collect tweets about Nairobi
    tweets = twitter.collect(query="Nairobi Kenya", limit=30)

    print(f"Collected {len(tweets)} tweets about Nairobi")

    # Display trending hashtags
    trending = twitter.collect_trending_hashtags()
    if trending:
        print(f"\nTrending hashtags in Nairobi:")
        for tag in trending[:10]:
            print(f"  {tag}")

    # Display sample tweets
    print(f"\nSample tweets:")
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"\n{i}. {tweet.title}")
        print(f"   Engagement: {tweet.metadata.get('engagement', 0)}")


def example_6_custom_report():
    """Example 6: Generate custom report."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Custom Report Generation")
    print("="*80 + "\n")

    orchestrator = NairobiInfoOrchestrator()

    # Collect and process
    items = orchestrator.collect_all(parallel=True)
    processor = DataProcessor()
    processed_items = processor.process(items)

    # Create report generator
    report_gen = ReportGenerator(output_dir='data')

    # Generate report for specific time period
    period_start = datetime.utcnow() - timedelta(hours=24)
    report = report_gen.generate_report(
        items=processed_items,
        period_start=period_start,
        title="Nairobi 24-Hour Brief"
    )

    # Save in different formats
    json_file = report_gen.save_as_json(report, filename='custom_report.json')
    md_file = report_gen.save_as_markdown(report, filename='custom_report.md')
    html_file = report_gen.save_as_html(report, filename='custom_report.html')

    print(f"Generated custom reports:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")
    print(f"  HTML: {html_file}")

    # Print summary
    report_gen.print_summary(report)


def example_7_high_impact_only():
    """Example 7: Filter for high-impact items only."""
    print("\n" + "="*80)
    print("EXAMPLE 7: High-Impact Items Only")
    print("="*80 + "\n")

    orchestrator = NairobiInfoOrchestrator()

    # Collect and process
    items = orchestrator.collect_all(parallel=True)
    processor = DataProcessor()
    processed_items = processor.process(items)

    # Filter for high-impact items
    high_impact = [
        item for item in processed_items
        if item.impact_level == 'high' or
        item.category == Category.BREAKING_UPDATES
    ]

    print(f"Total items: {len(processed_items)}")
    print(f"High-impact items: {len(high_impact)}")

    print(f"\nHigh-Impact Updates:")
    for i, item in enumerate(high_impact[:10], 1):
        print(f"\n{i}. [{item.category.value.upper()}] {item.title}")
        print(f"   {item.summary[:100]}...")
        print(f"   Relevance: {item.relevance_score:.2f} | {item.source_name}")


def main():
    """Run all examples."""
    examples = [
        ("Basic Collection", example_1_basic_collection),
        ("Single Source", example_2_single_source),
        ("Filter by Category", example_3_filter_by_category),
        ("Custom Processing", example_4_custom_processing),
        ("Twitter Only", example_5_twitter_only),
        ("Custom Report", example_6_custom_report),
        ("High-Impact Only", example_7_high_impact_only),
    ]

    print("\n" + "="*80)
    print("NAIROBI INFORMATION COLLECTOR - USAGE EXAMPLES")
    print("="*80)

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\n0. Run all examples")
    print("q. Quit")

    choice = input("\nSelect an example (0-7, q): ").strip()

    if choice.lower() == 'q':
        return

    try:
        if choice == '0':
            # Run all examples
            for name, example_func in examples:
                print(f"\n\nRunning: {name}")
                try:
                    example_func()
                except Exception as e:
                    print(f"Error in {name}: {e}")
                input("\nPress Enter to continue...")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Invalid choice")
    except ValueError:
        print("Invalid input")
    except KeyboardInterrupt:
        print("\n\nExecution stopped by user")


if __name__ == "__main__":
    main()
