def letter_grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


if __name__ == "__main__":
    print(letter_grade(95))  # A
    print(letter_grade(82))  # B
    print(letter_grade(70))  # C
    print(letter_grade(60))  # D
    print(letter_grade(55))  # F
