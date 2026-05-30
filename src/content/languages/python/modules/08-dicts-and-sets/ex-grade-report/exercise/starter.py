def passing_students(students, threshold):
    """
    Return a sorted list of names whose score >= threshold.
    students is a list of dicts: [{"name": ..., "score": ...}, ...]
    """
    # TODO: use a list comprehension to collect names where s["score"] >= threshold
    # Then wrap the result in sorted() and return it.
    pass


def class_average(students):
    """Return the average score rounded to 2 decimal places."""
    # TODO: collect all scores, compute sum / len, and round to 2 places.
    # Hint: [s["score"] for s in students] builds the list of scores.
    pass


def top_student(students):
    """Return the name of the student with the highest score."""
    # TODO: start with best = students[0], then loop over students.
    # If s["score"] > best["score"], update best = s.
    # Return best["name"] at the end.
    pass


if __name__ == "__main__":
    students = [
        {"name": "Ada",      "score": 88},
        {"name": "Grace",    "score": 95},
        {"name": "Linus",    "score": 72},
        {"name": "Margaret", "score": 95},
        {"name": "Guido",    "score": 60},
    ]
    print(passing_students(students, threshold=75))
    # ['Ada', 'Grace', 'Margaret']
    print(class_average(students))
    # 82.0
    print(top_student(students[:3]))
    # Grace
