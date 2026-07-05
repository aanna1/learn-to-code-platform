import csv


def load_grades(filepath):
    """Read a CSV with name/score columns and return a list of dicts.
    Each dict has 'name' (str) and 'score' (int).
    """
    grades = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grades.append({"name": row["name"], "score": int(row["score"])})
    return grades


def average_score(filepath):
    """Return the average score as a float rounded to 1 decimal place.
    Return 0.0 if there are no students.
    """
    grades = load_grades(filepath)
    if not grades:
        return 0.0
    total = sum(g["score"] for g in grades)
    return round(total / len(grades), 1)


if __name__ == "__main__":
    from pathlib import Path

    Path("grades.csv").write_text("name,score\nAlice,92\nBob,77\nCarol,88\n")

    print(load_grades("grades.csv"))
    print(average_score("grades.csv"))  # 85.7
