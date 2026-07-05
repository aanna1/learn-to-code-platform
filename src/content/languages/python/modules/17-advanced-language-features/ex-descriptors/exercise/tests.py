from submission import Clamped, AudioSettings


def test_audio_settings_normal_values():
    """AudioSettings stores in-range values as-is."""
    s = AudioSettings(50, 5)
    assert s.volume == 50 and s.bass == 5, (
        f"AudioSettings(50, 5) should give volume=50 bass=5, got volume={s.volume} bass={s.bass}."
    )


def test_volume_clamps_high():
    """Assigning above max clamps to max_val."""
    s = AudioSettings(50, 0)
    s.volume = 150
    assert s.volume == 100, (
        f"Setting volume=150 on AudioSettings should clamp to 100, got {s.volume}. "
        "Use max(min_val, min(max_val, value)) in __set__."
    )


def test_volume_clamps_low():
    """Assigning below min clamps to min_val."""
    s = AudioSettings(50, 0)
    s.volume = -5
    assert s.volume == 0, (
        f"Setting volume=-5 should clamp to 0, got {s.volume}."
    )


def test_bass_clamps_high():
    """Bass clamps to its own max_val (10)."""
    s = AudioSettings(50, 0)
    s.bass = 20
    assert s.bass == 10, (
        f"Setting bass=20 should clamp to 10, got {s.bass}."
    )


def test_bass_clamps_low():
    """Bass clamps to its own min_val (-10)."""
    s = AudioSettings(50, 0)
    s.bass = -99
    assert s.bass == -10, (
        f"Setting bass=-99 should clamp to -10, got {s.bass}."
    )


def test_clamps_on_init():
    """Clamping fires during __init__ too."""
    s = AudioSettings(999, -999)
    assert s.volume == 100 and s.bass == -10, (
        f"AudioSettings(999, -999) should clamp to volume=100 bass=-10, "
        f"got volume={s.volume} bass={s.bass}. "
        "self.volume = volume in __init__ goes through __set__, which should clamp."
    )


def test_default_before_assignment():
    """Reading a Clamped attribute before any assignment returns min_val."""
    class Widget:
        opacity = Clamped(0, 255)
    w = Widget()
    assert w.opacity == 0, (
        f"w.opacity before any assignment should return 0 (the min_val), got {w.opacity}. "
        "In __get__, use getattr(instance, self.private_name, self.min_val)."
    )


def test_two_instances_independent():
    """Each AudioSettings instance stores its own values independently."""
    a = AudioSettings(30, 3)
    b = AudioSettings(70, -3)
    assert a.volume == 30 and b.volume == 70, (
        f"Two AudioSettings instances should have independent values. "
        f"Got a.volume={a.volume}, b.volume={b.volume}. "
        "Store the value on the instance (via setattr), not on the descriptor itself."
    )
    a.volume = 10
    assert b.volume == 70, (
        "Changing a.volume should not affect b.volume. "
        "The descriptor must store values on each instance separately."
    )


def test_descriptor_on_class_returns_descriptor():
    """Accessing Clamped on the class (not an instance) returns the descriptor."""
    desc = AudioSettings.__dict__["volume"]
    assert isinstance(desc, Clamped), (
        "AudioSettings.volume (accessed via __dict__) should be the Clamped descriptor. "
        "Make sure __get__ returns self when instance is None."
    )


if __name__ == "__main__":
    s = AudioSettings(50, 5)
    print("volume:", s.volume, "bass:", s.bass)
    s.volume = 150
    print("clamped high:", s.volume)
    s.volume = -5
    print("clamped low:", s.volume)
