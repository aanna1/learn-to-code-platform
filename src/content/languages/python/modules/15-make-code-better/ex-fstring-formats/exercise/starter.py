def format_report(price: float, population: int, ratio: float, status_code: int, flags: int) -> str:
    # Replace each ... with the correct format spec
    line1 = f"Price:       ${price:...}"
    line2 = f"Population:  {population:...}"
    line3 = f"Ratio:       {ratio:...}"
    line4 = f"Status code: {status_code:...}"
    line5 = f"Flags:       {flags:...}"
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
