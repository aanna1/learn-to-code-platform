def passing_students(students, threshold):
    """
    Return a sorted list of names whose score >= threshold.
    """
    return sorted([s["name"] for s in students if s["score"] >= threshold])


def class_average(students):
    """Return the average score rounded to 2 decimal places."""
    scores = [s["score"] for s in students]
    return round(sum(scores) / len(scores), 2)


def top_student(students):
    """Return the name of the student with the highest score."""
    best = students[0]
    for s in students:
        if s["score"] > best["score"]:
            best = s
    return best["name"]


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
