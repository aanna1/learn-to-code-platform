def clamp(value, low, high):
    # TODO: return value clamped to the range [low, high]
    pass


if __name__ == "__main__":
    print(clamp(7, 0, 10))    # 7
    print(clamp(-3, 0, 10))   # 0
    print(clamp(15, 0, 10))   # 10
    print(clamp(0, 0, 10))    # 0
    print(clamp(10, 0, 10))   # 10
