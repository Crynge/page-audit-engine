#!/usr/bin/env python3
"""
CLI entry point for the Page-Level GEO/AEO/VEO Audit Engine.

Usage:
    python main.py --url "https://example.com/page" [--output report-name] [--verbose]

This module handles command-line argument parsing, audit execution,
and formatted output to both terminal and JSON file.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from audit_engine import AuditEngine
from config import Config, get_config


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Page-Level GEO/AEO/VEO Audit Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url "https://example.com/page"
  python main.py --url "https://example.com" --output my-audit
  python main.py --url "https://example.com" --verbose
        """,
    )

    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Target URL to audit (required)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output report filename (without .json extension). Default: audit-report-{timestamp}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    parser.add_argument(
        "--no-file",
        action="store_true",
        help="Skip saving report to file (terminal output only)",
    )

    return parser.parse_args()


def create_summary_table(report: Dict[str, Any]) -> Table:
    """Create a rich table summarizing the audit findings."""
    table = Table(title="📊 Audit Summary", show_header=True, header_style="bold magenta")

    table.add_column("Category", style="cyan", width=20)
    table.add_column("Count", style="yellow", width=8, justify="right")
    table.add_column("Preview", style="white", overflow="ellipsis")

    # Add rows for each finding category
    categories = [
        ("GEO Findings", report.get("geo_findings", [])),
        ("AEO Findings", report.get("aeo_findings", [])),
        ("VEO Findings", report.get("veo_findings", [])),
        ("Critical Errors", report.get("critical_errors", [])),
        ("Recommendations", report.get("recommendations", [])),
        ("Priority Fixes", report.get("priority_fixes", [])),
    ]

    for category_name, items in categories:
        count = len(items)
        preview = items[0][:50] + "..." if items and len(items[0]) > 50 else (items[0] if items else "-")
        table.add_row(category_name, str(count), preview)

    return table


def create_signals_panel(report: Dict[str, Any]) -> Panel:
    """Create a panel showing extracted page signals."""
    signals = report.get("page_signals", {})
    
    if not signals:
        return Panel("No page signals extracted", title="📄 Page Signals")

    signal_text = Text()
    signal_text.append("URL: ", style="bold")
    signal_text.append(f"{signals.get('url', 'N/A')}\n")
    signal_text.append("Status: ", style="bold")
    signal_text.append(f"{signals.get('status_code', 'N/A')}\n")
    signal_text.append("Title: ", style="bold")
    signal_text.append(f"{signals.get('title', 'N/A')[:60]}...\n" if len(signals.get('title', '')) > 60 else f"{signals.get('title', 'N/A')}\n")
    signal_text.append("Word Count: ", style="bold")
    signal_text.append(f"{signals.get('word_count', 0)}\n")
    signal_text.append("H1 Tags: ", style="bold")
    signal_text.append(f"{signals.get('h1_count', 0)}\n")
    signal_text.append("H2 Tags: ", style="bold")
    signal_text.append(f"{signals.get('h2_count', 0)}\n")
    signal_text.append("Schema Types: ", style="bold")
    signal_text.append(f"{', '.join(signals.get('schema_types', [])) or 'None'}\n")
    signal_text.append("Canonical: ", style="bold")
    signal_text.append(f"{signals.get('canonical_url', 'Not set')}\n")
    signal_text.append("Load Time: ", style="bold")
    signal_text.append(f"{signals.get('load_time_ms', 'N/A')}ms\n")

    return Panel(signal_text, title="📄 Page Signals")


def create_priority_fixes_table(report: Dict[str, Any]) -> Table:
    """Create a table showing priority fixes with color coding."""
    table = Table(title="🎯 Priority Fixes", show_header=True, header_style="bold red")

    table.add_column("Priority", style="bold", width=10)
    table.add_column("Fix", style="white", overflow="fold")

    priority_fixes = report.get("priority_fixes", [])

    for fix in priority_fixes:
        priority = "UNKNOWN"
        description = fix

        if fix.upper().startswith("HIGH:"):
            priority = "HIGH"
            description = fix[5:].strip()
        elif fix.upper().startswith("MEDIUM:"):
            priority = "MEDIUM"
            description = fix[7:].strip()
        elif fix.upper().startswith("LOW:"):
            priority = "LOW"
            description = fix[4:].strip()

        priority_style = {
            "HIGH": "bold red",
            "MEDIUM": "bold yellow",
            "LOW": "bold green",
        }.get(priority, "white")

        table.add_row(Text(priority, style=priority_style), description)

    return table


def print_terminal_output(report: Dict[str, Any], console: Console) -> None:
    """Print formatted audit results to terminal."""
    console.print()

    # Check for errors
    if "error" in report:
        error_panel = Panel(
            Text(f"⚠️  Audit Error: {report['error']}", style="bold red"),
            title="❌ Audit Failed",
            border_style="red",
        )
        console.print(error_panel)
        console.print()

    # Print page signals
    signals_panel = create_signals_panel(report)
    console.print(signals_panel)
    console.print()

    # Print summary table
    summary_table = create_summary_table(report)
    console.print(summary_table)
    console.print()

    # Print priority fixes if any exist
    if report.get("priority_fixes"):
        priority_table = create_priority_fixes_table(report)
        console.print(priority_table)
        console.print()

    # Final status
    if "error" not in report:
        success_panel = Panel(
            Text("✅ Audit completed successfully!", style="bold green"),
            border_style="green",
        )
        console.print(success_panel)


def save_report(report: Dict[str, Any], output_path: Path, console: Console) -> str:
    """
    Save audit report to JSON file.

    Args:
        report: Audit report dictionary.
        output_path: Path to save the report.
        console: Rich console for output.

    Returns:
        Path to saved file as string.
    """
    # Ensure reports directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    console.print(f"\n💾 Report saved to: {output_path}")
    return str(output_path)


def generate_output_filename(output_name: str | None) -> Path:
    """Generate output filename based on user input or timestamp."""
    reports_dir = Path(__file__).parent / "reports"

    if output_name:
        filename = f"{output_name}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"audit-report-{timestamp}.json"

    return reports_dir / filename


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    args = parse_arguments()
    setup_logging(args.verbose)

    console = Console()
    logger = logging.getLogger(__name__)

    # Print header
    console.print()
    console.print(Panel(
        Text("🔍 Page-Level GEO/AEO/VEO Audit Engine", style="bold cyan"),
        subtitle="Production-Ready Search Visibility Analysis",
    ))
    console.print()

    # Load configuration
    try:
        config = get_config()
        logger.debug("Configuration loaded successfully")
    except ValueError as e:
        error_panel = Panel(
            Text(str(e), style="bold red"),
            title="❌ Configuration Error",
            border_style="red",
        )
        console.print(error_panel)
        console.print("\n💡 Tip: Copy .env.example to .env and configure your API key")
        return 1

    # Generate output path
    output_path = generate_output_filename(args.output)
    logger.info(f"Output will be saved to: {output_path}")

    # Run audit
    console.print(f"🚀 Starting audit for: {args.url}")
    console.print()

    try:
        engine = AuditEngine(config)
        report = engine.run_audit(args.url)
    except Exception as e:
        logger.exception("Audit failed with exception")
        error_panel = Panel(
            Text(f"Fatal error: {str(e)}", style="bold red"),
            title="❌ Audit Failed",
            border_style="red",
        )
        console.print(error_panel)
        return 1

    # Print results to terminal
    print_terminal_output(report, console)

    # Save report to file (unless disabled)
    if not args.no_file:
        try:
            save_report(report, output_path, console)
        except IOError as e:
            logger.error(f"Failed to save report: {e}")
            console.print(f"\n⚠️  Warning: Could not save report to file: {e}")

    # Return appropriate exit code
    if "error" in report:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
