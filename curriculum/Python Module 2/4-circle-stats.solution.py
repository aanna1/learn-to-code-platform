import math


def circle_stats(radius):
    """Return (area, circumference) for a circle, both rounded to 2 decimal places."""
    area = round(math.pi * radius ** 2, 2)
    circumference = round(2 * math.pi * radius, 2)
    return (area, circumference)


if __name__ == "__main__":
    print(circle_stats(5))    # (78.54, 31.42)
    print(circle_stats(1))    # (3.14, 6.28)
    print(circle_stats(0))    # (0.0, 0.0)
    print(circle_stats(2.5))  # (19.63, 15.71)
