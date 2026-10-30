"""Summarize and optionally save a small expense ledger.

The report path is useful on its own. The optional SQLite export contains a
plausible API naming mistake that only appears when persistence is requested.
"""

import argparse
import sqlite3
from pathlib import Path

DEFAULT_EXPENSES = ("coffee:4.50", "lunch:12.00", "train:7.25")
SOURCE_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_DATABASE = SOURCE_DIRECTORY / "expenses.db"


def build_parser():
	parser = argparse.ArgumentParser(description="Summarize a day's expenses.")
	parser.add_argument(
		"expenses",
		nargs="*",
		help="Expenses in DESCRIPTION:AMOUNT format",
	)
	parser.add_argument(
		"--save",
		nargs="?",
		const=DEFAULT_DATABASE,
		metavar="DATABASE",
		help="Save to the program folder, or to DATABASE if provided",
	)
	return parser


def parse_expenses(raw_expenses):
	expenses = []
	for raw_expense in raw_expenses:
		try:
			description, raw_amount = raw_expense.rsplit(":", 1)
			amount = float(raw_amount)
		except ValueError as error:
			raise ValueError(
				f"Invalid expense {raw_expense!r}; use DESCRIPTION:AMOUNT."
			) from error

		if not description:
			raise ValueError("Expense descriptions cannot be empty.")
		if amount < 0:
			raise ValueError("Expense amounts cannot be negative.")
		expenses.append((description, amount))
	return expenses


def summarize(expenses):
	total = sum(amount for _, amount in expenses)
	return {
		"count": len(expenses),
		"total": total,
		"largest": max(expenses, key=lambda expense: expense[1]),
	}


def save_expenses(expenses, database):
	database = Path(database)
	if not database.is_absolute():
		database = SOURCE_DIRECTORY / database

	with sqlite3.connect(database) as connection:
		connection.execute(
			"CREATE TABLE IF NOT EXISTS expenses "
			"(description TEXT NOT NULL, amount REAL NOT NULL)"
		)
		connection.executemany(
			"INSERT INTO expenses (description, amount) VALUES (?, ?)",
			expenses,
		)
	return database


def main():
	args = build_parser().parse_args()
	expenses = parse_expenses(args.expenses or DEFAULT_EXPENSES)
	summary = summarize(expenses)
	largest_description, largest_amount = summary["largest"]
	print(f"Expenses: {summary['count']}")
	print(f"Total: ${summary['total']:.2f}")
	print(f"Largest: {largest_description} (${largest_amount:.2f})")

	if args.save:
		database = save_expenses(expenses, args.save)
		print(f"Saved to {database}")


if __name__ == "__main__":
	main()
