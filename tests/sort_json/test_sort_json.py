import json

import pytest

from cumulus_unit_test_utilities.sort_json.sort_json import sort_json_recursively, process_json_file


@pytest.fixture
def unsorted_json_from_dict():
    return json.loads(
        """
            {
                "z": 1,
                "a": {
                    "d": 4,
                    "b": 2
                },
                "m": [3, 2, 1]
            }
        """
    )


@pytest.fixture
def sorted_json_from_dict():
    return json.loads(
        """
            {
                "a": {
                    "b": 2,
                    "d": 4
                },
                "m": [3, 2, 1],
                "z": 1
            }
        """
    )


@pytest.fixture
def unsorted_json_from_list():
    return json.loads(
        """
            [
                {"foo": 1},
                {"bar": 2},
                {"baz": 3},
                {"qux": 4},
                {"corge": 5}
            ]
        """
    )


@pytest.fixture
def sorted_json_from_list():
    return json.loads(
        """
            [
                {"bar": 2},
                {"baz": 3},
                {"corge": 5},
                {"foo": 1},
                {"qux": 4}
            ]
        """
    )


def test_sort_json_recursively(
    unsorted_json_from_dict,
    unsorted_json_from_list,
    sorted_json_from_dict,
    sorted_json_from_list,
):
    generated_sort_from_dict = sort_json_recursively(unsorted_json_from_dict)
    generated_sort_from_list = sort_json_recursively(unsorted_json_from_list)

    assert generated_sort_from_dict == sorted_json_from_dict
    # I'm writing this assertion to show a potential gotcha when sorting the JSON with this function.
    assert not generated_sort_from_list == sorted_json_from_list


def test_process_json_file(unsorted_json_from_dict, unsorted_json_from_list, data_path):
    unsorted_changes = process_json_file(file_path=data_path / "unsorted.json", dry_run=True)
    sorted_bad_spacing_changes = process_json_file(file_path=data_path / "sorted_bad_spacing.json", dry_run=True)
    sorted_missing_eof_newline_changes = process_json_file(
        file_path=data_path / "sorted_missing_eof_newline.json",
        dry_run=True,
        print_diff=True,
    )
    sorted_changes = process_json_file(file_path=data_path / "sorted.json", dry_run=False)

    assert unsorted_changes
    assert sorted_bad_spacing_changes
    assert sorted_missing_eof_newline_changes
    assert not sorted_changes
