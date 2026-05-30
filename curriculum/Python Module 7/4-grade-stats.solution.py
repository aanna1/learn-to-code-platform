def grade_stats(grades):
    """Return (lowest, highest, average) for a list of grades."""
    lowest = min(grades)
    highest = max(grades)
    average = round(sum(grades) / len(grades), 2)
    return (lowest, highest, average)


if __name__ == "__main__":
    low, high, avg = grade_stats([85, 92, 78, 95, 88])
    print(f"Low: {low}, High: {high}, Avg: {avg}")
