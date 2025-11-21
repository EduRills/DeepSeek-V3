#!/usr/bin/env python3
"""
Nairobi Information Collector - Main Entry Point

Advanced Intelligence Retrieval Agent for collecting comprehensive
information about Nairobi, Kenya from multiple sources.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import NairobiInfoOrchestrator
from src.utils import setup_logger


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Nairobi Information Collector - Gather intelligence about Nairobi, Kenya"
    )

    parser.add_argument(
        '--mode',
        choices=['single', 'continuous'],
        default='single',
        help='Collection mode: single run or continuous'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Interval in minutes for continuous mode (default: 30)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--formats',
        nargs='+',
        choices=['json', 'markdown', 'html'],
        default=['json', 'markdown', 'html'],
        help='Output formats for reports'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    parser.add_argument(
        '--parallel',
        action='store_true',
        default=True,
        help='Run collections in parallel (default: True)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger(log_level=args.log_level, log_file='logs/nairobi_collector.log')

    print("=" * 80)
    print("NAIROBI INFORMATION COLLECTOR")
    print("Advanced Intelligence Retrieval Agent")
    print("=" * 80)
    print()

    try:
        # Initialize orchestrator
        orchestrator = NairobiInfoOrchestrator(config_path=args.config)

        if args.mode == 'single':
            print("Running single collection cycle...")
            print()

            result = orchestrator.run_collection_cycle(output_formats=args.formats)

            print()
            print("Collection Results:")
            print(f"  Items collected: {result['items_collected']}")
            print(f"  Duration: {result['duration_seconds']:.2f} seconds")
            print(f"  Output files:")
            for fmt, filepath in result['output_files'].items():
                print(f"    {fmt.upper()}: {filepath}")

        elif args.mode == 'continuous':
            print(f"Starting continuous collection (interval: {args.interval} minutes)")
            print("Press Ctrl+C to stop")
            print()

            orchestrator.run_continuous(interval_minutes=args.interval)

    except KeyboardInterrupt:
        print("\n\nCollection stopped by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
