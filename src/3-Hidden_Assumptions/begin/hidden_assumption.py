def remove_evens(numbers):
    for num in numbers[:]:
        if num % 2 == 0:
            numbers.remove(num)
    return numbers

# Testing operation
print(remove_evens([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))  # Expected output: [1, 3, 5, 7, 9]

print(remove_evens([1, 2, 3, 4, 4, 5, 7, 8, 9, 10]))  # Expected output: [1, 3, 5, 7, 9]