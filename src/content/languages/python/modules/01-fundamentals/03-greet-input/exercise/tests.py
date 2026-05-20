def test_includes_the_name():
    "greet_user('Ada') mentions the name"
    assert "Ada" in greet_user("Ada")


def test_full_message_for_ada():
    "greet_user('Ada') returns the full greeting"
    assert greet_user("Ada") == "Hi, Ada! Nice to meet you."


def test_works_for_another_name():
    "greet_user('Sam') greets Sam the same way"
    assert greet_user("Sam") == "Hi, Sam! Nice to meet you."
