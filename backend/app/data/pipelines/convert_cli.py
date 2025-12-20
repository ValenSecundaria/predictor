"""
Command-Line Interface for World Cup Data Conversion.

This module provides CLI commands to convert historical World Cup text data
to JSON format, validate existing data, and manage the conversion pipeline.

Location: backend/app/data/pipelines/convert_cli.py

Usage:
    python -m app.data.pipelines.convert_cli convert --year 1994
    python -m app.data.pipelines.convert_cli convert --all
    python -m app.data.pipelines.convert_cli validate --year 2014
    python -m app.data.pipelines.convert_cli list
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add parent directories to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.data.ingestion.text_parser import get_available_years
from app.data.pipelines.worldcup_converter import (
    convert_worldcup_year,
    convert_and_save_year,
    convert_all_years,
    save_worldcup_json,
)
from app.data.cleaning.match_validator import (
    validate_worldcup_json,
    validate_groups_json,
    ValidationResult,
)


# Default paths
DATASETS_DIR = SCRIPT_DIR.parent / "datasets"


def print_validation_result(result: ValidationResult, year: int) -> None:
    """Print validation result in a formatted way."""
    if result.is_valid:
        print(f"✅ {year}: Valid")
    else:
        print(f"❌ {year}: Invalid")
    
    if result.errors:
        print(f"   Errors ({len(result.errors)}):")
        for error in result.errors[:10]:  # Limit output
            print(f"     - {error}")
        if len(result.errors) > 10:
            print(f"     ... and {len(result.errors) - 10} more errors")
    
    if result.warnings:
        print(f"   Warnings ({len(result.warnings)}):")
        for warning in result.warnings[:5]:  # Limit output
            print(f"     - {warning}")
        if len(result.warnings) > 5:
            print(f"     ... and {len(result.warnings) - 5} more warnings")


def cmd_convert(args: argparse.Namespace) -> int:
    """Convert text files to JSON."""
    datasets_dir = Path(args.datasets_dir) if args.datasets_dir else DATASETS_DIR
    
    if not datasets_dir.exists():
        print(f"Error: Datasets directory not found: {datasets_dir}")
        return 1
    
    # Determine years to convert
    if args.all:
        years = get_available_years(datasets_dir)
        # Exclude 2014 and 2018 by default unless --force
        if not args.force:
            years = [y for y in years if y not in {2014, 2018}]
        print(f"Converting {len(years)} World Cup(s): {years}")
    elif args.year:
        years = [args.year]
        print(f"Converting World Cup {args.year}")
    else:
        print("Error: Specify --year YEAR or --all")
        return 1
    
    # Convert each year
    success_count = 0
    fail_count = 0
    
    for year in years:
        try:
            if args.dry_run:
                print(f"\n📋 Dry run for {year}:")
                worldcup_json, groups_json, validation = convert_worldcup_year(
                    datasets_dir, year
                )
                print(f"   Matches: {sum(len(r['matches']) for r in worldcup_json.get('rounds', []))}")
                print(f"   Groups: {len(groups_json.get('groups', []))}")
            else:
                print(f"\n🔄 Converting {year}...")
                validation = convert_and_save_year(datasets_dir, year)
                print(f"   ✅ Saved worldcup.json and worldcup.groups.json")
            
            print_validation_result(validation, year)
            
            if validation.is_valid:
                success_count += 1
            else:
                fail_count += 1
                
        except FileNotFoundError as e:
            print(f"\n❌ {year}: File not found - {e}")
            fail_count += 1
        except Exception as e:
            print(f"\n❌ {year}: Error - {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            fail_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Summary: {success_count} succeeded, {fail_count} failed")
    
    return 0 if fail_count == 0 else 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate existing JSON files."""
    datasets_dir = Path(args.datasets_dir) if args.datasets_dir else DATASETS_DIR
    
    if not datasets_dir.exists():
        print(f"Error: Datasets directory not found: {datasets_dir}")
        return 1
    
    # Determine years to validate
    if args.all:
        years = []
        for subdir in datasets_dir.iterdir():
            if subdir.is_dir() and subdir.name.isdigit():
                worldcup_json = subdir / "worldcup.json"
                if worldcup_json.exists():
                    years.append(int(subdir.name))
        years.sort()
        print(f"Validating {len(years)} World Cup(s): {years}")
    elif args.year:
        years = [args.year]
    else:
        print("Error: Specify --year YEAR or --all")
        return 1
    
    # Validate each year
    import json
    all_valid = True
    
    for year in years:
        year_dir = datasets_dir / str(year)
        worldcup_path = year_dir / "worldcup.json"
        groups_path = year_dir / "worldcup.groups.json"
        
        result = ValidationResult(is_valid=True)
        
        # Validate worldcup.json
        if worldcup_path.exists():
            try:
                with open(worldcup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                result.merge(validate_worldcup_json(data))
            except json.JSONDecodeError as e:
                result.add_error(f"Invalid JSON in worldcup.json: {e}")
        else:
            result.add_error(f"worldcup.json not found")
        
        # Validate worldcup.groups.json
        if groups_path.exists():
            try:
                with open(groups_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                result.merge(validate_groups_json(data))
            except json.JSONDecodeError as e:
                result.add_error(f"Invalid JSON in worldcup.groups.json: {e}")
        else:
            result.add_warning(f"worldcup.groups.json not found")
        
        print_validation_result(result, year)
        if not result.is_valid:
            all_valid = False
    
    return 0 if all_valid else 1


def cmd_list(args: argparse.Namespace) -> int:
    """List available World Cup years."""
    datasets_dir = Path(args.datasets_dir) if args.datasets_dir else DATASETS_DIR
    
    if not datasets_dir.exists():
        print(f"Error: Datasets directory not found: {datasets_dir}")
        return 1
    
    print("Available World Cup years:\n")
    print(f"{'Year':<8} {'cup.txt':<12} {'finals.txt':<12} {'JSON':<12}")
    print("-" * 44)
    
    for subdir in sorted(datasets_dir.iterdir()):
        if subdir.is_dir() and subdir.name.isdigit():
            year = subdir.name
            has_cup = "✅" if (subdir / "cup.txt").exists() else "❌"
            has_finals = "✅" if (subdir / "cup_finals.txt").exists() else "❌"
            has_json = "✅" if (subdir / "worldcup.json").exists() else "❌"
            
            print(f"{year:<8} {has_cup:<12} {has_finals:<12} {has_json:<12}")
    
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show statistics for a converted World Cup."""
    datasets_dir = Path(args.datasets_dir) if args.datasets_dir else DATASETS_DIR
    
    if not args.year:
        print("Error: Specify --year YEAR")
        return 1
    
    year_dir = datasets_dir / str(args.year)
    worldcup_path = year_dir / "worldcup.json"
    
    if not worldcup_path.exists():
        print(f"Error: No worldcup.json found for {args.year}")
        return 1
    
    import json
    with open(worldcup_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nWorld Cup {args.year} Statistics")
    print("=" * 40)
    
    rounds = data.get('rounds', [])
    total_matches = 0
    total_goals = 0
    knockout_matches = 0
    
    for round_data in rounds:
        round_name = round_data.get('name', 'Unknown')
        matches = round_data.get('matches', [])
        round_goals = 0
        
        for match in matches:
            total_matches += 1
            if match.get('knockout'):
                knockout_matches += 1
            
            goals1 = len(match.get('goals1', []))
            goals2 = len(match.get('goals2', []))
            round_goals += goals1 + goals2
        
        total_goals += round_goals
        print(f"{round_name}: {len(matches)} matches, {round_goals} goals")
    
    print("-" * 40)
    print(f"Total: {total_matches} matches, {total_goals} goals recorded")
    print(f"Group stage: {total_matches - knockout_matches} matches")
    print(f"Knockout stage: {knockout_matches} matches")
    print(f"Average goals per match: {total_goals / total_matches:.2f}" if total_matches > 0 else "")
    
    return 0


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="World Cup Data Conversion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Convert 1994 World Cup:
    python -m app.data.pipelines.convert_cli convert --year 1994
    
  Convert all available (except 2014/2018):
    python -m app.data.pipelines.convert_cli convert --all
    
  Dry run (show what would be done):
    python -m app.data.pipelines.convert_cli convert --all --dry-run
    
  Validate existing JSON:
    python -m app.data.pipelines.convert_cli validate --year 2014
    
  List available years:
    python -m app.data.pipelines.convert_cli list
        """
    )
    
    parser.add_argument(
        '--datasets-dir', '-d',
        help='Path to datasets directory'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert text to JSON')
    convert_parser.add_argument('--year', '-y', type=int, help='Year to convert')
    convert_parser.add_argument('--all', '-a', action='store_true', help='Convert all years')
    convert_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    convert_parser.add_argument('--force', '-f', action='store_true', help='Include 2014/2018')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate JSON files')
    validate_parser.add_argument('--year', '-y', type=int, help='Year to validate')
    validate_parser.add_argument('--all', '-a', action='store_true', help='Validate all years')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available years')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--year', '-y', type=int, help='Year to analyze')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        sys.exit(cmd_convert(args))
    elif args.command == 'validate':
        sys.exit(cmd_validate(args))
    elif args.command == 'list':
        sys.exit(cmd_list(args))
    elif args.command == 'stats':
        sys.exit(cmd_stats(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
