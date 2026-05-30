def grade_stats(grades):
    """Return (lowest, highest, average) for a list of grades."""
    # TODO: compute lowest using min()
    lowest = ...

    # TODO: compute highest using max()
    highest = ...

    # TODO: compute the average and round it to 2 decimal places
    average = ...

    # TODO: return a tuple of (lowest, highest, average)
    pass


if __name__ == "__main__":
    low, high, avg = grade_stats([85, 92, 78, 95, 88])
    print(f"Low: {low}, High: {high}, Avg: {avg}")
