`sort_json` sorts a JSON file or directory of JSON files alphabetically and recursively by keys. It edits the files in place ensuring that they will be spaced with 4 indentations and end with a single blank line.

```aiignore
$ sort_json --help
usage: sort_json [-h] [--dry-run] [--print-diff] path

Recursively sort JSON files.

positional arguments:
  path          Path or glob pattern to JSON file(s), e.g. '*.json' or '**/*.json'

options:
  -h, --help    show this help message and exit
  --dry-run     Show which files would be changed without modifying them
  --print-diff  Print diff without performing changes
```
