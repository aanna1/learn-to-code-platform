def filter_numbers(numbers):
    result = []
    for n in numbers:
        if n < 0:
            continue
        if n > 100:
            break
        result.append(n)
    return result


if __name__ == "__main__":
    print(filter_numbers([3, -1, 7, -4, 200, 9]))  # [3, 7]
    print(filter_numbers([10, 20, 30]))              # [10, 20, 30]
