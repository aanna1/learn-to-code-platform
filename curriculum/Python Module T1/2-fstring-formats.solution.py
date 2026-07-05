def format_report(price: float, population: int, ratio: float, status_code: int, flags: int) -> str:
    line1 = f"Price:       ${price:.2f}"
    line2 = f"Population:  {population:,}"
    line3 = f"Ratio:       {ratio:.1%}"
    line4 = f"Status code: {status_code:#x}"
    line5 = f"Flags:       {flags:08b}"
    return "\n".join([line1, line2, line3, line4, line5])


if __name__ == "__main__":
    report = format_report(
        price=3.14159,
        population=1234567,
        ratio=0.847,
        status_code=255,
        flags=42,
    )
    print(report)
