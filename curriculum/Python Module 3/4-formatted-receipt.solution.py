coffee = 3.50
avocado_toast = 12.75
orange_juice = 4.00

# Sum the three prices — never hardcode the total
total = coffee + avocado_toast + orange_juice

# Header: item name left-aligned in 22 chars, label right-aligned in 8 chars
print(f"{'Item':<22}{'Price':>8}")

# Separator: 30 dashes (22 + 8 = 30 matches the column widths)
print("-" * 30)

# Each item: name left-aligned in 22 chars, price right-aligned in 8 chars, 2 decimal places
print(f"{'Coffee':<22}{coffee:>8.2f}")
print(f"{'Avocado toast':<22}{avocado_toast:>8.2f}")
print(f"{'Orange juice':<22}{orange_juice:>8.2f}")

print("-" * 30)

# Total line uses the same format
print(f"{'Total':<22}{total:>8.2f}")
