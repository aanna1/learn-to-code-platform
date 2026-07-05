class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    @property
    def gpa(self):
        return sum(self.grades) / len(self.grades)

    def __repr__(self):
        return f"Student(name={self.name!r}, gpa={self.gpa:.1f})"

    def __lt__(self, other):
        return self.gpa < other.gpa

    def add_grade(self, score):
        self.grades.append(score)


if __name__ == "__main__":
    students = [
        Student("Alice", [88, 92, 95]),
        Student("Bob",   [77, 85]),
        Student("Carol", [99, 96, 92]),
    ]
    print(sorted(students))
    # [Student(name='Bob', gpa=81.0), Student(name='Alice', gpa=91.7), Student(name='Carol', gpa=95.7)]
