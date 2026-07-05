def test_rectangle_area():
    "Rectangle area is width * height"
    r = Rectangle(4, 6)
    assert r.area() == 24, f"Rectangle(4, 6).area() should be 24, got {r.area()!r}."

def test_rectangle_perimeter():
    "Rectangle perimeter is 2 * (width + height)"
    r = Rectangle(4, 6)
    assert r.perimeter() == 20, f"Rectangle(4, 6).perimeter() should be 20, got {r.perimeter()!r}."

def test_rectangle_is_square_false():
    "Rectangle.is_square() returns False when width != height"
    r = Rectangle(4, 6)
    assert r.is_square() == False, (
        "Rectangle(4, 6).is_square() should return False."
    )

def test_rectangle_is_square_true():
    "Rectangle.is_square() returns True when width == height"
    r = Rectangle(5, 5)
    assert r.is_square() == True, (
        "Rectangle(5, 5).is_square() should return True."
    )

def test_rectangle_str():
    "Rectangle __str__ includes both dimensions"
    r = Rectangle(4, 6)
    s = str(r)
    assert "4" in s and "6" in s, (
        f"str(Rectangle(4, 6)) should contain '4' and '6', got: {s!r}"
    )

def test_square_inherits_area():
    "Square.area() works via inheritance (no re-implementation needed)"
    s = Square(5)
    assert s.area() == 25, f"Square(5).area() should be 25, got {s.area()!r}."

def test_square_inherits_perimeter():
    "Square.perimeter() works via inheritance"
    s = Square(5)
    assert s.perimeter() == 20, f"Square(5).perimeter() should be 20, got {s.perimeter()!r}."

def test_square_is_square():
    "Square.is_square() returns True via inheritance"
    s = Square(5)
    assert s.is_square() == True, "Square(5).is_square() should return True."

def test_square_str_contains_side():
    "Square __str__ includes the side length"
    s = Square(5)
    assert "5" in str(s), f"str(Square(5)) should contain '5', got: {str(s)!r}"

def test_square_is_instance_of_rectangle():
    "Square is an instance of Rectangle (inheritance check)"
    s = Square(5)
    assert isinstance(s, Rectangle), (
        "Square should inherit from Rectangle. Use: class Square(Rectangle):"
    )

def test_square_width_and_height_equal():
    "Square sets width and height equal via super().__init__"
    s = Square(7)
    assert s.width == 7 and s.height == 7, (
        f"Square(7) should have width=7 and height=7, got width={s.width!r}, height={s.height!r}. "
        "Did you call super().__init__(side, side)?"
    )
