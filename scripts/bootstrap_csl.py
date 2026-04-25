#!/usr/bin/env python3
"""Bootstrap CSL files for Quarto/Pandoc workflows.

Defaults to APA (`apa.csl`) from the official CSL repository.
Users can select another official CSL style name or provide a custom CSL source URL.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

OFFICIAL_STYLES_RAW_BASE = (
    "https://raw.githubusercontent.com/citation-style-language/styles/master"
)
DEFAULT_STYLE = "apa"
DEFAULT_OUTPUT_DIR = Path("academic-paper/templates/csl")


def _normalize_style_name(style: str) -> str:
    normalized = style.strip().lower()
    if normalized.endswith(".csl"):
        normalized = normalized[:-4]
    return normalized


def _resolve_source_url(style: str, custom_source: str | None) -> str:
    if custom_source:
        return custom_source
    return f"{OFFICIAL_STYLES_RAW_BASE}/{style}.csl"


def _ask_style_interactively(default_style: str) -> str:
    print("Choose citation style for CSL bootstrap.")
    print(f"Press Enter to use default: {default_style}.csl")
    entered = input("Style name (e.g., apa, ieee, chicago-author-date): ").strip()
    if not entered:
        return default_style
    return _normalize_style_name(entered)


def _download_csl(source_url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(source_url, timeout=20) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Failed to download CSL (HTTP {exc.code}) from: {source_url}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download CSL from: {source_url} ({exc.reason})") from exc

    destination.write_bytes(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download a CSL file into academic-paper/templates/csl/."
    )
    parser.add_argument(
        "--style",
        default=None,
        help=(
            "CSL style name from the official repository, without .csl "
            "(default: interactive prompt with apa fallback)"
        ),
    )
    parser.add_argument(
        "--source-url",
        default=None,
        help="Custom direct URL to a .csl file (for non-official/custom styles).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directory to store CSL files (default: {DEFAULT_OUTPUT_DIR}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    style = _normalize_style_name(args.style) if args.style else _ask_style_interactively(DEFAULT_STYLE)
    if not style:
        print("Error: style name cannot be empty.", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    destination = output_dir / f"{style}.csl"
    source_url = _resolve_source_url(style, args.source_url)

    try:
        _download_csl(source_url, destination)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Downloaded {style}.csl to {destination}")
    print(f"Source: {source_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
