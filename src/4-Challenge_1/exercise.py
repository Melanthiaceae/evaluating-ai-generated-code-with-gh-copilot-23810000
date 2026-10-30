"""Split a restaurant bill, including tax and tip, among friends."""

import math


def get_non_negative_float(prompt: str) -> float:
	while True:
		try:
			value = float(input(prompt))
		except ValueError:
			print("Please enter a valid number.")
			continue
		if not math.isfinite(value):
			print("Please enter a finite number.")
			continue
		if value < 0:
			print("Please enter a non-negative value.")
			continue
		return value


def get_positive_int(prompt: str) -> int:
	while True:
		try:
			value = int(input(prompt))
		except ValueError:
			print("Please enter a valid whole number.")
			continue
		if value <= 0:
			print("Please enter a positive number of people.")
			continue
		return value


def confirm_rate(name: str, rate: float) -> float:
	while rate > 30:
		confirmation = input(
			f"{name} rate is {rate:.2f}%. Are you sure you want to continue? (yes/no): "
		).strip().lower()
		if confirmation in ("y", "yes"):
			break
		rate = get_non_negative_float(f"New {name.lower()} percentage: ")
	return rate


def main() -> None:
	bill = get_non_negative_float("Bill amount: $")
	tax_rate = get_non_negative_float("Tax percentage: ")
	tip_rate = get_non_negative_float("Tip percentage: ")
	people = get_positive_int("Number of people: ")

	tax_rate = confirm_rate("Tax", tax_rate)
	tip_rate = confirm_rate("Tip", tip_rate)

	tax = bill * tax_rate / 100
	tip = bill * tip_rate / 100
	total = bill + tax + tip

	print(f"Tax: ${tax:.2f}")
	print(f"Tip: ${tip:.2f}")
	print(f"Total: ${total:.2f}")

	total_cents = round(total * 100)
	share_cents, extra_cent_people = divmod(total_cents, people)
	if extra_cent_people:
		print(
			f"To make the total add up, {extra_cent_people} "
			f"{'person' if extra_cent_people == 1 else 'people'} should pay "
			f"${(share_cents + 1) / 100:.2f} and "
			f"{people - extra_cent_people} "
			f"{'person' if people - extra_cent_people == 1 else 'people'} should pay "
			f"${share_cents / 100:.2f}."
		)
	else:
		print(f"Each person pays: ${share_cents / 100:.2f}")


if __name__ == "__main__":
	main()
