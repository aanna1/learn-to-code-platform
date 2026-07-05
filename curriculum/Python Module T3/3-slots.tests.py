from submission import Vector3, Pixel, try_bad_attr


def test_vector3_magnitude_basic():
    """Vector3.magnitude() returns the correct Euclidean length."""
    v = Vector3(1.0, 2.0, 2.0)
    result = v.magnitude()
    assert abs(result - 3.0) < 1e-9, (
        f"Vector3(1, 2, 2).magnitude() should be 3.0, got {result}. "
        "Use (x**2 + y**2 + z**2) ** 0.5."
    )


def test_vector3_magnitude_zero():
    """Vector3(0, 0, 0).magnitude() is 0.0."""
    v = Vector3(0.0, 0.0, 0.0)
    assert v.magnitude() == 0.0, (
        f"Vector3(0,0,0).magnitude() should be 0.0, got {v.magnitude()}."
    )


def test_vector3_magnitude_unit():
    """Vector3(1, 0, 0).magnitude() is 1.0."""
    v = Vector3(1.0, 0.0, 0.0)
    assert abs(v.magnitude() - 1.0) < 1e-9, (
        f"Vector3(1,0,0).magnitude() should be 1.0, got {v.magnitude()}."
    )


def test_vector3_repr():
    """Vector3.__repr__ returns 'Vector3(x, y, z)'."""
    v = Vector3(1.0, 2.0, 3.0)
    result = repr(v)
    assert result == "Vector3(1.0, 2.0, 3.0)", (
        f"repr(Vector3(1.0, 2.0, 3.0)) should be 'Vector3(1.0, 2.0, 3.0)', got {result!r}. "
        "Use an f-string: f'Vector3({self.x}, {self.y}, {self.z})'."
    )


def test_vector3_no_dict():
    """Vector3 instances have no __dict__ (slots are active)."""
    v = Vector3(1.0, 2.0, 3.0)
    assert not hasattr(v, "__dict__"), (
        "Vector3 instances should have no __dict__. "
        "Make sure __slots__ = ('x', 'y', 'z') is set at class level."
    )


def test_vector3_bad_attr_blocked():
    """Assigning an undeclared attribute to Vector3 raises AttributeError."""
    v = Vector3(1.0, 2.0, 3.0)
    result = try_bad_attr(v)
    assert result == "blocked", (
        f"try_bad_attr(Vector3(...)) should return 'blocked', got {result!r}. "
        "With __slots__, undeclared attributes raise AttributeError."
    )


def test_pixel_defaults():
    """Pixel() defaults all channels to 0."""
    p = Pixel()
    assert p.r == 0 and p.g == 0 and p.b == 0, (
        f"Pixel() should default to r=0, g=0, b=0, got r={p.r}, g={p.g}, b={p.b}."
    )


def test_pixel_values():
    """Pixel stores r, g, b correctly."""
    p = Pixel(255, 128, 0)
    assert p.r == 255 and p.g == 128 and p.b == 0, (
        f"Pixel(255, 128, 0) should give r=255 g=128 b=0, got r={p.r} g={p.g} b={p.b}."
    )


def test_pixel_no_dict():
    """Pixel instances have no __dict__ (slots=True is active)."""
    p = Pixel(1, 2, 3)
    assert not hasattr(p, "__dict__"), (
        "Pixel instances should have no __dict__. "
        "Make sure you used @dataclass(slots=True), not just @dataclass."
    )


def test_pixel_bad_attr_blocked():
    """Assigning an undeclared attribute to Pixel raises AttributeError."""
    p = Pixel()
    result = try_bad_attr(p)
    assert result == "blocked", (
        f"try_bad_attr(Pixel()) should return 'blocked', got {result!r}. "
        "With slots=True, undeclared attributes raise AttributeError."
    )


def test_try_bad_attr_allowed_on_normal_class():
    """try_bad_attr returns 'allowed' for a plain class without slots."""
    class Plain:
        pass
    result = try_bad_attr(Plain())
    assert result == "allowed", (
        f"try_bad_attr(Plain()) should return 'allowed' since Plain has no slots, got {result!r}."
    )


if __name__ == "__main__":
    v = Vector3(1.0, 2.0, 2.0)
    print("magnitude:", v.magnitude())
    print("repr:", repr(v))
    print("has __dict__:", hasattr(v, "__dict__"))
    print("bad attr:", try_bad_attr(v))
    p = Pixel(255, 128, 0)
    print("pixel:", p.r, p.g, p.b)
