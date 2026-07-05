import csv


def load_grades(filepath):
    """Read a CSV with name/score columns and return a list of dicts.
    Each dict has 'name' (str) and 'score' (int).
    """
    # Open the file and use csv.DictReader
    # Cast row["score"] to int before adding each row
    pass


def average_score(filepath):
    """Return the average score as a float rounded to 1 decimal place.
    Return 0.0 if there are no students.
    """
    pass


if __name__ == "__main__":
    from pathlib import Path

    # Create a sample CSV to test with
    Path("grades.csv").write_text("name,score\nAlice,92\nBob,77\nCarol,88\n")

    print(load_grades("grades.csv"))
    # [{'name': 'Alice', 'score': 92}, {'name': 'Bob', 'score': 77}, {'name': 'Carol', 'score': 88}]

    print(average_score("grades.csv"))
    # 85.7
