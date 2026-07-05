class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        # TODO: return width * height
        pass

    def perimeter(self):
        # TODO: return 2 * (width + height)
        pass

    def is_square(self):
        # TODO: return True if width == height
        pass

    def __str__(self):
        # TODO: return a string like Rectangle(4 x 6)
        pass


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    def __str__(self):
        # TODO: return a string like Square(5)
        pass


if __name__ == "__main__":
    r = Rectangle(4, 6)
    print(r)
    print(r.area())
    print(r.perimeter())
    print(r.is_square())

    s = Square(5)
    print(s)
    print(s.area())
    print(s.is_square())
