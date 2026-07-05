class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    @property
    def gpa(self):
        # TODO: return the average of self.grades
        pass

    def __repr__(self):
        # TODO: return a string like Student(name='Alice', gpa=91.7)
        pass

    def __lt__(self, other):
        # TODO: return True if this student's GPA is less than the other's
        pass

    def add_grade(self, score):
        # TODO: append score to self.grades
        pass


if __name__ == "__main__":
    students = [
        Student("Alice", [88, 92, 95]),
        Student("Bob",   [77, 85]),
        Student("Carol", [99, 96, 92]),
    ]
    print(sorted(students))
