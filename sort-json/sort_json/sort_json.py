import difflib
import glob
import os
import sys
import json
import argparse
from colorama import Fore, Style


# Python supported emojis can be found here
# https://carpedm20.github.io/emoji/


def sort_json_recursively(obj: dict | list) -> dict | list:
    if isinstance(obj, dict):
        return {k: sort_json_recursively(obj[k]) for k in sorted(obj)}
    elif isinstance(obj, list):
        return [sort_json_recursively(elem) for elem in obj]
    else:
        return obj


def process_json_file(file_path, dry_run=False, print_diff=False) -> bool:
    change_detected = False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        sorted_data = sort_json_recursively(original_data)
        new_json_string = json.dumps(sorted_data, indent=4, ensure_ascii=False)

        if not new_json_string.endswith("\n"):
            new_json_string += "\n"

        with open(file_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        if current_content != new_json_string:
            change_detected = True
            if dry_run:
                print(f"\N{RIGHT-POINTING MAGNIFYING GLASS} DRY RUN: Would modify {file_path}")
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
                            print(Fore.CYAN + line + Style.RESET_ALL, end="")
                        elif line.startswith("!"):
                            print(Fore.YELLOW + line + Style.RESET_ALL, end="")
                        elif line.startswith("+"):
                            print(Fore.GREEN + line + Style.RESET_ALL, end="")
                        elif line.startswith("-"):
                            print(Fore.RED + line + Style.RESET_ALL, end="")
                        else:
                            print(line, end="")

            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_json_string)
                print(f"\N{WHITE HEAVY CHECK MARK} Sorted: {file_path}")
        else:
            if dry_run:
                print(f"\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16} DRY RUN: No changes needed for {file_path}")
    except Exception as e:
        print(f"\N{CROSS MARK} Error processing {file_path}: {e}")

    return change_detected


def process_path(pattern, dry_run=False, print_diff=False) -> bool:
    changes_detected = set()
    matched_files = glob.glob(pattern, recursive=True)

    if not matched_files:
        print(f"\N{CROSS MARK} No files matched pattern: {pattern}")
        return False

    for file_path in matched_files:
        if os.path.isfile(file_path) and file_path.endswith(".json"):
            changes_detected.add(process_json_file(file_path, dry_run, print_diff))

    return any(changes_detected)


def main():
    parser = argparse.ArgumentParser(description="Recursively sort JSON files.")
    parser.add_argument("path", help="Path or glob pattern to JSON file(s), e.g. '*.json' or '**/*.json'")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show which files would be changed without modifying them"
    )
    parser.add_argument("--print-diff", action="store_true", help="Print diff without performing changes")

    args = parser.parse_args()
    print(f"Checking path: {args.path}")
    changes_detected = process_path(args.path, dry_run=args.dry_run, print_diff=args.print_diff)
    if args.dry_run and changes_detected:
        print("\N{HEAVY EXCLAMATION MARK SYMBOL} Dry run detected improperly formatted JSON files.")
        print("-" * 103)
        sys.exit(1)
    elif args.dry_run and not changes_detected:
        print("\N{WHITE HEAVY CHECK MARK} Dry run detected no improperly formatted JSON files.")
        print("-" * 103)


if __name__ == "__main__":
    main()
