import argparse
import difflib
import glob
import json
import os
import sys
from typing import Any, Optional

from colorama import Fore, Style

# Python supported emojis can be found here
# https://carpedm20.github.io/emoji/

INDENT = 4


def sort_json_recursively(obj: Any, parent_key: Optional[str] = None, sort_lists_by: Optional[dict] = None) -> Any:
    sort_rules = sort_lists_by or {}

    if isinstance(obj, dict):
        sorted_dict = {}
        for k in sorted(obj):
            v = obj[k]
            sorted_dict[k] = sort_json_recursively(v, parent_key=k, sort_lists_by=sort_rules)
        return sorted_dict
    elif isinstance(obj, list):
        # Sort if the parent key matches a sort rule
        if parent_key in sort_rules:
            sort_key = sort_rules[parent_key]
            obj = sorted(obj, key=lambda x: x[sort_key])
        return [sort_json_recursively(elem, sort_lists_by=sort_rules) for elem in obj]
    else:
        return obj


def process_json_file(file_path, dry_run=False, print_diff=False, sort_lists_by: Optional[dict] = None) -> bool:
    change_detected = False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        sorted_data = sort_json_recursively(original_data, sort_lists_by=sort_lists_by)
        new_json_string = json.dumps(sorted_data, indent=4, ensure_ascii=False)

        if not new_json_string.endswith("\n"):
            new_json_string += "\n"

        with open(file_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        if current_content != new_json_string:
            change_detected = True
            if dry_run:
                print(f"\N{RIGHT-POINTING MAGNIFYING GLASS} DRY RUN: Would modify {file_path}", file=sys.stderr)
                if print_diff:
                    diff = difflib.context_diff(
                        current_content.splitlines(keepends=True),
                        new_json_string.splitlines(keepends=True),
                        fromfile="original",
                        tofile="sorted",
                        lineterm="\n",
                    )
                    for line in diff:
                        if line.startswith("***") or line.startswith("---"):
                            print(Fore.CYAN + line + Style.RESET_ALL, end="", file=sys.stderr)
                        elif line.startswith("!"):
                            print(Fore.YELLOW + line + Style.RESET_ALL, end="", file=sys.stderr)
                        elif line.startswith("+"):
                            print(Fore.GREEN + line + Style.RESET_ALL, end="", file=sys.stderr)
                        elif line.startswith("-"):
                            print(Fore.RED + line + Style.RESET_ALL, end="", file=sys.stderr)
                        else:
                            print(line, end="", file=sys.stderr)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_json_string)
                print(f"\N{WHITE HEAVY CHECK MARK} Sorted: {file_path}")
        else:
            if dry_run:
                print(
                    f"\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16} DRY RUN: No changes needed for {file_path}",
                    file=sys.stderr,
                )
    except Exception as e:
        print(f"\N{CROSS MARK} Error processing {file_path}: {e}", file=sys.stderr)

    return change_detected


def process_path(pattern, dry_run=False, print_diff=False, sort_lists_by: Optional[str] = None) -> bool:
    changes_detected = set()
    matched_files = glob.glob(pattern, recursive=True)

    if not matched_files:
        print(f"\N{CROSS MARK} No files matched pattern: {pattern}", file=sys.stderr)
        return False

    for file_path in matched_files:
        if os.path.isfile(file_path) and file_path.endswith(".json"):
            changes_detected.add(process_json_file(file_path, dry_run, print_diff, sort_lists_by))

    return any(changes_detected)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recursively sort JSON files.")
    parser.add_argument("path", help="Path or glob pattern to JSON file(s), e.g. '*.json' or '**/*.json'")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which files would be changed without modifying them",
    )
    parser.add_argument(
        "--sort-rules",
        type=str,
        help='JSON string of rules, e.g. \'{"Candies": "name", "Vegetables": "type"}\'',
    )
    parser.add_argument("--print-diff", action="store_true", help="Print diff without performing changes")

    return parser


def main(args: Optional[argparse.Namespace] = None) -> None:
    """
    Entry point that handles both direct Namespace injection (tests)
    and sys.argv parsing (production).
    """
    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.sort_rules:
        try:
            sort_lists_by = json.loads(args.sort_rules)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON provided for --sort-rules: {args.sort_rules}", file=sys.stderr)
            sys.exit(1)
    else:
        sort_lists_by = None

    print(f"Checking path: {args.path}", file=sys.stderr)
    changes_detected = process_path(
        args.path,
        dry_run=args.dry_run,
        print_diff=args.print_diff,
        sort_lists_by=sort_lists_by,
    )
    if args.dry_run and changes_detected:
        print("\N{HEAVY EXCLAMATION MARK SYMBOL} Dry run detected improperly formatted JSON files.", file=sys.stderr)
        print("-" * 103, file=sys.stderr)
        sys.exit(1)
    elif args.dry_run and not changes_detected:
        print("\N{WHITE HEAVY CHECK MARK} Dry run detected no improperly formatted JSON files.", file=sys.stderr)
        print("-" * 103, file=sys.stderr)
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
