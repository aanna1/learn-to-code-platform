class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height

    def __str__(self):
        return f"Rectangle({self.width} x {self.height})"


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    def __str__(self):
        return f"Square({self.width})"


if __name__ == "__main__":
    r = Rectangle(4, 6)
    print(r)              # Rectangle(4 x 6)
    print(r.area())       # 24
    print(r.perimeter())  # 20
    print(r.is_square())  # False

    s = Square(5)
    print(s)              # Square(5)
    print(s.area())       # 25
    print(s.is_square())  # True
