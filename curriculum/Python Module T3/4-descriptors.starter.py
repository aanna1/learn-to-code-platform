class Clamped:
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
        self.private_name = ""  # filled in by __set_name__

    def __set_name__(self, owner, name):
        # TODO: store the private name, e.g. "_volume" for "volume"
        pass

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # TODO: return the stored value, defaulting to self.min_val if not set
        pass

    def __set__(self, instance, value):
        # TODO: clamp value to [min_val, max_val] and store on instance
        pass


class AudioSettings:
    volume = Clamped(0, 100)
    bass = Clamped(-10, 10)

    def __init__(self, volume: int, bass: int) -> None:
        self.volume = volume
        self.bass = bass


if __name__ == "__main__":
    s = AudioSettings(50, 5)
    print(s.volume, s.bass)    # 50 5
    s.volume = 150
    print(s.volume)            # 100
    s.volume = -5
    print(s.volume)            # 0
    s.bass = 20
    print(s.bass)              # 10

    class Widget:
        opacity = Clamped(0, 255)
    w = Widget()
    print(w.opacity)           # 0
