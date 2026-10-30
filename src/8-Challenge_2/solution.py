import argparse
import csv
import io
import sys
import unicodedata
from pathlib import Path


def _terminal_cell(value):
    value = value.replace("\n", " / ")
    escaped = []
    for character in value:
        category = unicodedata.category(character)
        if character == "\t":
            escaped.append(r"\t")
        elif character == "\r":
            escaped.append(r"\r")
        elif category.startswith("C"):
            codepoint = ord(character)
            escaped.append(f"\\x{codepoint:02x}" if codepoint <= 0xFF else f"\\u{codepoint:04x}")
        else:
            escaped.append(character)
    return "".join(escaped)


def _terminal_width(value):
    width = 0
    for character in value:
        if unicodedata.category(character) in ("Mn", "Me"):
            continue
        width += 2 if unicodedata.east_asian_width(character) in ("W", "F") else 1
    return width


def parse_csv(csv_text):
    """Parse CSV text, rejecting input that doesn't appear to be comma-separated."""
    try:
        rows = list(csv.reader(io.StringIO(csv_text), strict=True))
    except csv.Error as error:
        raise ValueError(
            f"CSV parsing failed: {error}. Check for unclosed quotes or malformed quoted fields."
        ) from error

    if not any(row for row in rows):
        raise ValueError("The input is empty. Provide CSV text with at least one row.")

    if not any(len(row) > 1 for row in rows):
        raise ValueError(
            "The input does not appear to be comma-separated; no row has multiple columns. "
            "Add commas between columns, and surround fields containing commas with double quotes."
        )

    return rows


def csv_to_markdown(csv_text):
    """Convert CSV text into a Markdown table."""
    rows = parse_csv(csv_text)
    column_count = max(map(len, rows))
    rows = [row + [""] * (column_count - len(row)) for row in rows]

    def escape(value):
        return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")

    header = "| " + " | ".join(escape(cell) for cell in rows[0]) + " |"
    separator = "| " + " | ".join("---" for _ in range(column_count)) + " |"
    body = ["| " + " | ".join(escape(cell) for cell in row) + " |" for row in rows[1:]]
    return "\n".join([header, separator, *body]) + "\n"


def csv_to_table(csv_text):
    """Convert CSV text into a plain-text table for terminal output."""
    rows = parse_csv(csv_text)
    column_count = max(map(len, rows))
    rows = [row + [""] * (column_count - len(row)) for row in rows]
    rows = [[_terminal_cell(cell) for cell in row] for row in rows]
    column_widths = [
        max(_terminal_width(row[column]) for row in rows)
        for column in range(column_count)
    ]

    border = "+" + "+".join("-" * (width + 2) for width in column_widths) + "+"

    def format_row(row):
        cells = [
            cell + " " * (width - _terminal_width(cell))
            for cell, width in zip(row, column_widths)
        ]
        return "| " + " | ".join(cells) + " |"

    table_rows = [border, format_row(rows[0]), border]
    table_rows.extend(format_row(row) for row in rows[1:])
    table_rows.append(border)
    return "\n".join(table_rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Render CSV data as a Markdown file or terminal table.")
    parser.add_argument("input", help="CSV file path, CSV text, or '-' to read CSV text from stdin")
    parser.add_argument("-o", "--output", help="Markdown output path (default: <input-name>.md or output.md)")
    parser.add_argument("-cli", action="store_true", help="print a plain-text table to the terminal instead")
    args = parser.parse_args()

    if args.cli and args.output:
        parser.error("-o/--output cannot be used with -cli.")

    input_path = Path(args.input)
    if args.input == "-":
        csv_text = sys.stdin.read()
        default_output = Path("output.md")
    elif input_path.is_file():
        if input_path.suffix.lower() != ".csv":
            print("Input rejected: the input file must have a .csv extension.", file=sys.stderr)
            return 2
        csv_text = input_path.read_text(encoding="utf-8-sig")
        default_output = input_path.with_suffix(".md")
    elif input_path.suffix.lower() == ".csv":
        print(f"Input rejected: missing file: {args.input}", file=sys.stderr)
        return 2
    else:
        csv_text = args.input
        default_output = Path("output.md")

    try:
        rendered = csv_to_table(csv_text) if args.cli else csv_to_markdown(csv_text)
    except ValueError as error:
        print(f"Input rejected: {error}", file=sys.stderr)
        return 2

    if args.cli:
        print(rendered, end="")
        return 0

    output_path = Path(args.output) if args.output else default_output
    if output_path.suffix.lower() != ".md":
        output_path = Path(f"{output_path}.md")
    output_path.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())