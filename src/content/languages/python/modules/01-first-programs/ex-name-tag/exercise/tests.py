def test_first_name():
    "first_name is a non-empty, single-word string"
    assert isinstance(first_name, str), (
        f"first_name should be a string, got {type(first_name).__name__}. "
        "Assign it like: first_name = \"Ada\""
    )
    assert first_name.strip(), "first_name is empty — give it a real first name."
    assert " " not in first_name, (
        f"first_name should be a single first name with no spaces, got: {first_name!r}"
    )


def test_last_name():
    "last_name is a non-empty, single-word string"
    assert isinstance(last_name, str), (
        f"last_name should be a string, got {type(last_name).__name__}."
    )
    assert last_name.strip(), "last_name is empty — give it a real last name."
    assert " " not in last_name, (
        f"last_name should be a single last name with no spaces, got: {last_name!r}"
    )


def test_city():
    "city is a non-empty string"
    assert isinstance(city, str), f"city should be a string, got {type(city).__name__}."
    assert city.strip(), "city is empty — give it a real city name."
