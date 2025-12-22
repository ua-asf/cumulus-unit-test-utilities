import argparse
import json

import pytest

from sort_json.sort_json import main, process_json_file, sort_json_recursively

diff_symbol = "***"


@pytest.fixture
def unsorted_json_from_dict():
    return {
        "z": 1,
        "a": {
            "d": 4,
            "b": 2,
        },
        "candies": [
            {
                "name": "good candy",
                "quantity": 100,
            },
            {
                "name": "mediocre candy",
                "quantity": 50,
            },
            {
                "name": "bad candy",
                "quantity": 2,
            },
        ],
    }


@pytest.fixture
def sorted_json_from_dict():
    return {
        "a": {
            "b": 2,
            "d": 4,
        },
        "candies": [
            {
                "name": "bad candy",
                "quantity": 2,
            },
            {
                "name": "good candy",
                "quantity": 100,
            },
            {
                "name": "mediocre candy",
                "quantity": 50,
            },
        ],
        "z": 1,
    }


@pytest.fixture
def unsorted_json_from_list():
    return [
        {"foo": 1},
        {"bar": 2},
        {"baz": 3},
        {"qux": 4},
        {"corge": 5},
    ]


@pytest.fixture
def sorted_json_from_list():
    return [
        {"bar": 2},
        {"baz": 3},
        {"corge": 5},
        {"foo": 1},
        {"qux": 4},
    ]


def test_sort_json_recursively(
    unsorted_json_from_dict,
    unsorted_json_from_list,
    sorted_json_from_dict,
    sorted_json_from_list,
):
    generated_sort_from_dict = sort_json_recursively(unsorted_json_from_dict, sort_lists_by={"candies": "name"})
    generated_sort_from_list = sort_json_recursively(unsorted_json_from_list)

    assert generated_sort_from_dict == sorted_json_from_dict
    # I'm writing this assertion to show a potential gotcha when sorting the JSON with this function.
    # Namely, that a common key must exist to sort by.
    assert generated_sort_from_list != sorted_json_from_list


def test_process_json_file(unsorted_json_from_dict, unsorted_json_from_list, data_path):
    unsorted_changes = process_json_file(file_path=data_path / "unsorted.json", dry_run=True)
    sorted_bad_spacing_changes = process_json_file(file_path=data_path / "sorted_bad_spacing.json", dry_run=True)
    sorted_missing_eof_newline_changes = process_json_file(
        file_path=data_path / "sorted_missing_eof_newline.json",
        dry_run=True,
        print_diff=False,
    )
    sorted_changes = process_json_file(file_path=data_path / "sorted.json", dry_run=False)

    assert unsorted_changes
    assert sorted_bad_spacing_changes
    assert sorted_missing_eof_newline_changes
    assert not sorted_changes


def test_main(
    tmp_path,
    unsorted_json_from_dict,
    sorted_json_from_dict,
    capsys,
    monkeypatch,
):
    # Integration test
    unsorted_dir = tmp_path / "unsorted"
    unsorted_dir.mkdir()

    sorted_dir = tmp_path / "sorted"
    sorted_dir.mkdir()
    sorted_files_path = str(sorted_dir / "*.json")
    unsorted_files_path = str(unsorted_dir / "*.json")
    indent = 4

    unsorted_from_dict_file = unsorted_dir / "unsorted_json_from_dict.json"
    unsorted_from_dict_file.write_text(json.dumps(unsorted_json_from_dict, indent=indent) + "\n")
    sorted_from_dict_file = sorted_dir / "sorted_json_from_dict.json"
    sorted_from_dict_file.write_text(json.dumps(sorted_json_from_dict, indent=indent) + "\n")

    # --- Scenario 1: Dry run, NO errors detected (Expected: Exit Code 0, Success Message) ---
    args_1 = argparse.Namespace(
        path=sorted_files_path,
        dry_run=True,
        sort_rules=None,
        print_diff=False,
    )

    with pytest.raises(SystemExit) as excinfo:
        main(args_1)

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Dry run detected no improperly formatted JSON files." in captured.err

    # --- Scenario 2: Dry run, WITH errors detected, NO print-diff
    # (Expected: Exit Code 1, Failure Message, No Diff Output) ---
    args_2 = argparse.Namespace(path=unsorted_files_path, dry_run=True, sort_rules=None, print_diff=False)

    with pytest.raises(SystemExit) as excinfo:
        main(args_2)

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    # Should see the error message but NO diff symbols
    assert "Dry run detected improperly formatted JSON files." in captured.err
    assert diff_symbol not in captured.err

    # --- Scenario 3: Repeat of Scenario 2 WITH print-diff (Expected: Exit Code 1, Failure Message, Diff Output) ---
    args_2 = argparse.Namespace(
        path=unsorted_files_path,
        dry_run=True,
        sort_rules=None,
        print_diff=True,
    )

    with pytest.raises(SystemExit) as excinfo:
        main(args_2)

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    # Should see the error message WITH diff symbols
    assert "Dry run detected improperly formatted JSON files." in captured.err
    assert diff_symbol not in captured.out
    assert diff_symbol in captured.err

    # --- Scenario 4: Repeat of Scenario 2 but without passing in args, to test create_parser()
    # (Expected: Exit Code 1, Failure Message, No Diff Output) ---
    # Instead of creating a Namespace, create a list of strings
    # This simulates exactly what a user types: "sort-json <path> --dry-run"
    test_argv = ["sort-json", str(unsorted_from_dict_file), "--dry-run"]

    monkeypatch.setattr("sys.argv", test_argv)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    # Should see the error message but NO diff symbol
    assert "Dry run detected improperly formatted JSON files." in captured.err
    assert diff_symbol not in captured.err

    # --- Scenario 5: Repeat of Scenario 4 WITH print-dif
    # (Expected: Exit Code 1, Failure Message, Diff Output) ---
    # Instead of creating a Namespace, create a list of strings
    # This simulates exactly what a user types: "sort-json <path> --dry-run"
    test_argv = ["sort-json", str(unsorted_from_dict_file), "--dry-run", "--print-diff"]

    monkeypatch.setattr("sys.argv", test_argv)

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    # Should see the error message AND diff symbol
    assert "Dry run detected improperly formatted JSON files." in captured.err
    assert diff_symbol not in captured.out
    assert diff_symbol in captured.err

    # --- Scenario 6: Valid --sort-rules and non-dry-run
    # (Expected: Exit Code 0, No extra message, File on disk modified) ---
    test_rules = '{"candies": "name"}'
    args_3 = argparse.Namespace(path=unsorted_files_path, dry_run=False, sort_rules=test_rules, print_diff=False)

    with pytest.raises(SystemExit) as excinfo:
        main(args_3)

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert f"Checking path: {unsorted_files_path}" in captured.err
    # Main will modify the files that you send to it directly
    assert unsorted_from_dict_file.read_text() == sorted_from_dict_file.read_text()

    # --- Scenario 7: Invalid JSON for --sort-rules (Expected: ValueError) ---
    args_4 = argparse.Namespace(path=sorted_files_path, dry_run=False, sort_rules='{"bad_json": ', print_diff=False)

    with pytest.raises(SystemExit) as excinfo:
        main(args_4)

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Invalid JSON provided for --sort-rules:" in captured.err
