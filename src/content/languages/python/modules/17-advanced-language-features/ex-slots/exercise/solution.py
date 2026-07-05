from dataclasses import dataclass


class Vector3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __repr__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"


@dataclass(slots=True)
class Pixel:
    r: int = 0
    g: int = 0
    b: int = 0


def try_bad_attr(obj) -> str:
    try:
        obj.nonexistent = True
        return "allowed"
    except AttributeError:
        return "blocked"


if __name__ == "__main__":
    v = Vector3(1.0, 2.0, 2.0)
    print(v.magnitude())            # 3.0
    print(repr(v))                  # Vector3(1.0, 2.0, 2.0)
    print(hasattr(v, "__dict__"))   # False
    print(try_bad_attr(v))          # blocked

    p = Pixel(255, 128, 0)
    print(p.r, p.g, p.b)           # 255 128 0
    print(hasattr(p, "__dict__"))   # False
    print(try_bad_attr(p))          # blocked
