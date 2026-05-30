word = "extraordinary"

# First character: position 0
print(word[0])

# Last character: -1 counts from the end
print(word[-1])

# First five characters: positions 0-4, stop is exclusive so use 5
print(word[:5])

# Everything from position 5 onward: omit the stop to go to the end
print(word[5:])

# Reversed: step of -1 walks the string backward
print(word[::-1])

# Positions 6 through 9 inclusive: stop must be 10 because stop is exclusive
print(word[6:10])
