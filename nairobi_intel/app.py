from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Optional

from .collector import IntelCollector
from .models import Category


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Nairobi Intelligence Brief")
    parser.add_argument("--stub", action="store_true", help="Include stubbed offline data")
    parser.add_argument(
        "--category",
        choices=[c.value for c in Category],
        help="Limit the brief to a single category",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip network fetches and rely on stubbed data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the brief to a file instead of stdout",
    )
    return parser.parse_args()


def write_output(text: str, output: Optional[Path]) -> None:
    if output:
        output.write_text(text)
    else:
        print(text)


def main() -> None:
    args = parse_args()
    collector = IntelCollector()

    async def run() -> str:
        if args.category:
            brief = await collector.collect_by_category(
                Category(args.category), include_stub=args.stub, skip_network=args.offline
            )
        else:
            brief = await collector.collect(include_stub=args.stub, skip_network=args.offline)
        return brief.to_report()

    text = asyncio.run(run())
    write_output(text, args.output)


if __name__ == "__main__":
    main()
