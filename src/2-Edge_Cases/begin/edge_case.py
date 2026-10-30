import json
from pathlib import Path


TODO_FILE = Path(__file__).resolve().parent / "tasks.json"


def load_tasks():
	"""Load tasks from disk, treating a missing or empty file as no tasks."""
	if not TODO_FILE.exists():
		return []

	try:
		with TODO_FILE.open("r", encoding="utf-8") as file:
			tasks = json.load(file)
		return tasks if isinstance(tasks, list) else []
	except (json.JSONDecodeError, OSError):
		return []


def save_tasks(tasks):
	with TODO_FILE.open("w", encoding="utf-8") as file:
		json.dump(tasks, file, indent=2)


def read_input(prompt):
	try:
		return input(prompt).strip()
	except EOFError:
		return ""


def next_id(tasks):
	ids = [task.get("id", 0) for task in tasks if isinstance(task, dict)]
	return max(ids, default=0) + 1


def display_tasks(tasks):
	print("\nCurrent tasks:")
	if not tasks:
		print("No tasks.")
		return
	for task in tasks:
		print(f'{task["id"]}: {task["description"]}')


def main():
	tasks = load_tasks()

	while True:
		print("\n1. View tasks\n2. Add task\n3. Remove task\n4. Quit")
		choice = read_input("Choose an option: ")

		if choice == "1":
			display_tasks(tasks)
		elif choice == "2":
			description = read_input("Enter a task: ")
			if description:
				tasks.append({"id": next_id(tasks), "description": description})
				save_tasks(tasks)
				print("Task added.")
			else:
				print("Task cannot be empty.")
		elif choice == "3":
			try:
				task_id = int(read_input("Enter the task ID to remove: "))
			except ValueError:
				print("Invalid ID.")
				continue
			remaining = [task for task in tasks if task.get("id") != task_id]
			if len(remaining) == len(tasks):
				print("Task not found.")
			else:
				tasks = remaining
				save_tasks(tasks)
				print("Task removed.")
		elif choice == "4":
			break
		else:
			print("Invalid option.")


if __name__ == "__main__":
	main()
