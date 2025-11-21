"""Main orchestrator for coordinating data collection and report generation."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.scrapers import NewsScraper, GovernmentScraper, TourismScraper
from src.collectors import TwitterCollector, InstagramCollector, YouTubeCollector
from src.processors import DataProcessor, ReportGenerator
from src.models import InformationItem, ReliabilityLevel
from src.utils import load_config, get_logger, setup_logger


class NairobiInfoOrchestrator:
    """
    Main orchestrator for collecting and processing Nairobi information.

    Coordinates:
    - Web scrapers for news, government, and tourism sites
    - Social media collectors for Twitter, Instagram, YouTube
    - Data processing and verification
    - Report generation
    """

    def __init__(self, config_path: str = None):
        """
        Initialize the orchestrator.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)

        # Setup logging
        setup_logger(
            log_level=self.config.get('app', {}).get('log_level', 'INFO'),
            log_file='logs/nairobi_collector.log'
        )

        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing Nairobi Info Orchestrator")

        # Initialize components
        self.scrapers = self._init_scrapers()
        self.collectors = self._init_collectors()
        self.processor = DataProcessor(
            min_relevance_score=0.3,
            max_age_hours=72
        )
        self.report_generator = ReportGenerator(output_dir='data')

        self.logger.info("Orchestrator initialized successfully")

    def _init_scrapers(self) -> List:
        """Initialize web scrapers."""
        scrapers = []

        # News scrapers
        news_sources = self.config.get('sources', {}).get('news', [])
        for source in news_sources:
            if source.get('enabled', True):
                scraper = NewsScraper(
                    source_name=source['name'],
                    base_url=source['url'],
                    reliability=ReliabilityLevel.HIGH if source.get('priority') == 'high' else ReliabilityLevel.MEDIUM
                )
                scrapers.append(scraper)

        # Government scrapers
        gov_sources = self.config.get('sources', {}).get('government', [])
        for source in gov_sources:
            if source.get('enabled', True):
                scraper = GovernmentScraper(
                    source_name=source['name'],
                    base_url=source['url'],
                    reliability=ReliabilityLevel.VERIFIED
                )
                scrapers.append(scraper)

        # Tourism scrapers
        tourism_sources = self.config.get('sources', {}).get('tourism', [])
        for source in tourism_sources:
            if source.get('enabled', True):
                scraper = TourismScraper(
                    source_name=source['name'],
                    base_url=source['url'],
                    reliability=ReliabilityLevel.MEDIUM
                )
                scrapers.append(scraper)

        self.logger.info(f"Initialized {len(scrapers)} scrapers")
        return scrapers

    def _init_collectors(self) -> List:
        """Initialize social media collectors."""
        collectors = []

        # Twitter collector
        try:
            twitter = TwitterCollector()
            collectors.append(twitter)
        except Exception as e:
            self.logger.warning(f"Failed to initialize Twitter collector: {e}")

        # Instagram collector
        try:
            instagram = InstagramCollector()
            collectors.append(instagram)
        except Exception as e:
            self.logger.warning(f"Failed to initialize Instagram collector: {e}")

        # YouTube collector
        try:
            youtube = YouTubeCollector()
            collectors.append(youtube)
        except Exception as e:
            self.logger.warning(f"Failed to initialize YouTube collector: {e}")

        self.logger.info(f"Initialized {len(collectors)} collectors")
        return collectors

    def collect_all(self, parallel: bool = True) -> List[InformationItem]:
        """
        Collect information from all sources.

        Args:
            parallel: Run collections in parallel (default: True)

        Returns:
            List of all collected items
        """
        self.logger.info("Starting collection from all sources")
        start_time = datetime.utcnow()

        all_items = []

        if parallel:
            all_items = self._collect_parallel()
        else:
            all_items = self._collect_sequential()

        duration = (datetime.utcnow() - start_time).total_seconds()
        self.logger.info(f"Collection complete: {len(all_items)} items in {duration:.2f}s")

        return all_items

    def _collect_parallel(self) -> List[InformationItem]:
        """Collect from all sources in parallel."""
        all_items = []

        # Use ThreadPoolExecutor for parallel collection
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []

            # Submit scraper tasks
            for scraper in self.scrapers:
                future = executor.submit(self._safe_scrape, scraper)
                futures.append(future)

            # Submit collector tasks
            for collector in self.collectors:
                future = executor.submit(self._safe_collect, collector)
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    items = future.result()
                    all_items.extend(items)
                except Exception as e:
                    self.logger.error(f"Error in parallel collection: {e}")

        return all_items

    def _collect_sequential(self) -> List[InformationItem]:
        """Collect from all sources sequentially."""
        all_items = []

        # Scrapers
        for scraper in self.scrapers:
            items = self._safe_scrape(scraper)
            all_items.extend(items)

        # Collectors
        for collector in self.collectors:
            items = self._safe_collect(collector)
            all_items.extend(items)

        return all_items

    def _safe_scrape(self, scraper) -> List[InformationItem]:
        """Safely execute a scraper with error handling."""
        try:
            self.logger.info(f"Scraping: {scraper.source_name}")
            items = scraper.scrape()
            self.logger.info(f"Scraped {len(items)} items from {scraper.source_name}")
            return items
        except Exception as e:
            self.logger.error(f"Error scraping {scraper.source_name}: {e}")
            return []

    def _safe_collect(self, collector) -> List[InformationItem]:
        """Safely execute a collector with error handling."""
        try:
            self.logger.info(f"Collecting from: {collector.platform_name}")
            items = collector.collect(query="Nairobi", limit=50)
            self.logger.info(f"Collected {len(items)} items from {collector.platform_name}")
            return items
        except Exception as e:
            self.logger.error(f"Error collecting from {collector.platform_name}: {e}")
            return []

    def process_and_generate_report(
        self,
        items: List[InformationItem],
        output_formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Process items and generate reports.

        Args:
            items: List of items to process
            output_formats: List of output formats (json, markdown, html)

        Returns:
            Dictionary mapping format to file path
        """
        if output_formats is None:
            output_formats = ['json', 'markdown', 'html']

        self.logger.info(f"Processing {len(items)} items")

        # Process items
        processed_items = self.processor.process(items)

        self.logger.info(f"Processed: {len(processed_items)} items remain")

        # Get statistics
        stats = self.processor.get_statistics(processed_items)
        self.logger.info(f"Statistics: {stats}")

        # Generate report
        period_start = datetime.utcnow() - timedelta(hours=72)
        report = self.report_generator.generate_report(
            items=processed_items,
            period_start=period_start
        )

        # Save in requested formats
        output_files = {}

        if 'json' in output_formats:
            filepath = self.report_generator.save_as_json(report)
            output_files['json'] = filepath

        if 'markdown' in output_formats:
            filepath = self.report_generator.save_as_markdown(report)
            output_files['markdown'] = filepath

        if 'html' in output_formats:
            filepath = self.report_generator.save_as_html(report)
            output_files['html'] = filepath

        # Print summary
        self.report_generator.print_summary(report)

        return output_files

    def run_collection_cycle(self, output_formats: List[str] = None) -> Dict[str, Any]:
        """
        Run a complete collection cycle.

        Args:
            output_formats: Output formats for reports

        Returns:
            Dictionary with collection results
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting new collection cycle")
        self.logger.info("=" * 80)

        start_time = datetime.utcnow()

        # Collect data
        items = self.collect_all(parallel=True)

        # Process and generate reports
        output_files = self.process_and_generate_report(items, output_formats)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        result = {
            'start_time': start_time.isoformat(),
            'duration_seconds': duration,
            'items_collected': len(items),
            'output_files': output_files,
            'success': True
        }

        self.logger.info("=" * 80)
        self.logger.info(f"Collection cycle complete in {duration:.2f}s")
        self.logger.info("=" * 80)

        return result

    def run_continuous(self, interval_minutes: int = 30):
        """
        Run continuous collection at specified intervals.

        Args:
            interval_minutes: Interval between collections in minutes
        """
        self.logger.info(f"Starting continuous collection mode (interval: {interval_minutes} min)")

        while True:
            try:
                # Run collection cycle
                self.run_collection_cycle()

                # Wait for next cycle
                self.logger.info(f"Waiting {interval_minutes} minutes until next collection...")
                import time
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                self.logger.info("Stopping continuous collection")
                break
            except Exception as e:
                self.logger.error(f"Error in continuous collection: {e}")
                # Wait before retrying
                import time
                time.sleep(60)
