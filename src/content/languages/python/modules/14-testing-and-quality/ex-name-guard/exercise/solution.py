def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32


def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9


def main():
    print(f"0°C = {celsius_to_fahrenheit(0)}°F")
    print(f"100°C = {celsius_to_fahrenheit(100)}°F")
    print(f"32°F = {fahrenheit_to_celsius(32)}°C")
    print(f"212°F = {fahrenheit_to_celsius(212)}°C")


if __name__ == "__main__":
    main()
