def sum_range(start, stop):
    total = 0
    for n in range(start, stop + 1):
        total += n
    return total


if __name__ == "__main__":
    print(sum_range(1, 5))    # 15
    print(sum_range(1, 100))  # 5050
