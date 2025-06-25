import pytest
from typing import List, Dict, Any
from file_manager import is_parsed_correctly, check_required_keys, \
    REQUIRED_KEYS


# Define test cases
@pytest.mark.parametrize("objects, expected_result", [
    ([{'mode': 'white'}, {"type": "line", "coords": [0, 0], "fill": "black",
                          "width": 1}], True),  # Valid line object
    ([{'mode': 'green'}, {"type": "rectangle", "coords": [0, 0, 10, 10],
                          "fill": "blue", "width": 1, "outline": "red"}],
     False),  # Invalid mode key
    ([{'mode': 'white'},
      {"type": "rectangle", "coords": [0, 0, 10, 10], "fill": "blue",
       "width": 1, "outline": "red"}], True),  # Valid rectangle object
    ([{'mode': 'white'},
      {"type": "oval", "coords": [0, 0, 10, 10], "fill": "green",
       "width": 1, "outline": "black"}], True),  # Valid oval object
    ([{'mode': 'black'},
      {"type": "polygon", "coords": [[0, 0], [10, 0], [10, 10]],
       "fill": "yellow", "width": 1, "outline": "blue"}], True),
    # Valid polygon object
    ([{'mode': 'white'},
      {"type": "text", "coords": [0, 0], "fill": "white", "text": "Hello",
       "font": "Arial"}], True),  # Valid text object
    ([{'mode': 'white'}, {"type": "invalid_type", "coords": [0, 0],
                          "fill": "black"}], False),  # Invalid type
    ([{'mode': 'white'}, {"type": "line", "coords": [0, 0],
                          "fill": "black"}], False),
    # Missing width for the line object
    ([{'mode': 'white'}, {"type": "rectangle", "coords": [0, 0, 10, 10],
                          "fill": "blue", "outline": "red"}], False),
    # Missing width for the rectangle object
    ([{'mode': 'white'}, {"type": "text", "coords": [0, 0], "fill": "white",
                          "font": "Arial"}], False),
    # Missing text for the text object
    ([{'mode': 'white'},
      {"type": "line", "coords": [0, 0], "fill": "black", "width": 1},
      {"type": "invalid_type"}], False)  # Mixed valid and invalid objects
])
def test_is_parsed_right(objects: List[Dict[str, Any]],
                         expected_result: bool) -> None:
    assert is_parsed_correctly(objects) == expected_result


def test_check_required_keys() -> None:
    # Test case where all required keys are present
    obj1 = {"type": "line", "coords": (0, 0, 100, 100), "fill": "red",
            "width": 2}
    assert check_required_keys(obj1, REQUIRED_KEYS["line"])

    # Test case where some required keys are missing
    obj2 = {"type": "rectangle", "coords": (0, 0, 100, 100), "fill": "blue"}
    assert not check_required_keys(obj2, REQUIRED_KEYS["rectangle"])


def test_check_required_keys_all_present() -> None:
    # Test case where all required keys are present
    obj = {"type": "line", "coords": (0, 0, 100, 100), "fill": "red",
           "width": 2}
    required_keys = ["type", "coords", "fill", "width"]
    assert check_required_keys(obj, required_keys)


def test_check_required_keys_some_missing() -> None:
    # Test case where some required keys are missing
    obj = {"type": "rectangle", "coords": (0, 0, 100, 100), "fill": "blue"}
    required_keys = ["type", "coords", "fill", "width"]
    assert not check_required_keys(obj, required_keys)


def test_check_required_keys_empty_object() -> None:
    # Test case where the object is empty
    obj: Dict[str, Any] = {}
    required_keys: List[str] = ["type", "coords", "fill", "width"]
    assert not check_required_keys(obj, required_keys)


def test_check_required_keys_empty_required_keys() -> None:
    # Test case where required_keys list is empty
    obj: Dict[str, Any] = {"type": "line", "coords": (0, 0, 100, 100),
                           "fill": "red", "width": 2}
    required_keys: List[str] = []
    assert check_required_keys(obj, required_keys)


def test_check_required_keys_both_empty() -> None:
    # Test case where both object and required_keys list are empty
    obj: Dict[str, Any] = {}
    required_keys: List[str] = []
    assert check_required_keys(obj, required_keys)


def test_is_parsed_correctly() -> None:
    # Test case where JSON is parsed correctly
    objects1 = [
        {'mode': 'white'},
        {"type": "line", "coords": (0, 0, 100, 100), "fill": "red",
         "width": 2},
        {"type": "rectangle", "coords": (0, 0, 100, 100), "fill": "blue",
         "width": 2, "outline": "black"}
    ]
    assert is_parsed_correctly(objects1)

    # Test case where JSON is not parsed correctly
    objects2 = [
        {'mode': 'white'},
        {"type": "line", "coords": (0, 0, 100, 100), "fill": "red",
         "width": 2},
        {"type": "rectangle", "fill": "blue", "width": 2, "outline": "black"}
    ]
    assert not is_parsed_correctly(objects2)

    # Test case where JSON is not parsed correctly
    objects3 = [
        {'mode': 'blue'},
        {"type": "line", "coords": (0, 0, 100, 100), "fill": "red",
         "width": 2},
        {"type": "rectangle", "coords": (0, 0, 100, 100), "fill": "blue",
         "width": 2, "outline": "black"}
    ]
    assert not is_parsed_correctly(objects3)


if __name__ == "__main__":
    pytest.main()  # Run tests
