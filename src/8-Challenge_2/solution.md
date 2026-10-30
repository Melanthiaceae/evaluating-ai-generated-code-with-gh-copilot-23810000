| import argparse |  |  |  |
| --- | --- | --- | --- |
| import csv |  |  |  |
| import io |  |  |  |
| import sys |  |  |  |
| from pathlib import Path |  |  |  |
|  |  |  |  |
|  |  |  |  |
| def parse_csv(csv_text): |  |  |  |
|     """Parse CSV text |  rejecting input that doesn't appear to be comma-separated.""" |  |  |
|     try: |  |  |  |
|         rows = list(csv.reader(io.StringIO(csv_text) |  strict=True)) |  |  |
|     except csv.Error as error: |  |  |  |
|         raise ValueError( |  |  |  |
|             f"CSV parsing failed: {error}. Check for unclosed quotes or malformed quoted fields." |  |  |  |
|         ) from error |  |  |  |
|  |  |  |  |
|     if not any(row for row in rows): |  |  |  |
|         raise ValueError("The input is empty. Provide CSV text with at least one row.") |  |  |  |
|  |  |  |  |
|     if not any(len(row) > 1 for row in rows): |  |  |  |
|         raise ValueError( |  |  |  |
|             "The input does not appear to be comma-separated; no row has multiple columns. " |  |  |  |
|             "Add commas between columns |  and surround fields containing commas with double quotes." |  |  |
|         ) |  |  |  |
|  |  |  |  |
|     return rows |  |  |  |
|  |  |  |  |
|  |  |  |  |
| def csv_to_markdown(csv_text): |  |  |  |
|     """Convert CSV text into a Markdown table.""" |  |  |  |
|     rows = parse_csv(csv_text) |  |  |  |
|     column_count = max(map(len |  rows)) |  |  |
|     rows = [row + [""] * (column_count - len(row)) for row in rows] |  |  |  |
|  |  |  |  |
|     def escape(value): |  |  |  |
|         return str(value).replace("\\\\" |  "\\\\\\\\").replace("\|" |  "\\\\\|").replace("\\n" |  "<br>") |
|  |  |  |  |
|     header = "\| " + " \| ".join(escape(cell) for cell in rows[0]) + " \|" |  |  |  |
|     separator = "\| " + " \| ".join("---" for _ in range(column_count)) + " \|" |  |  |  |
|     body = ["\| " + " \| ".join(escape(cell) for cell in row) + " \|" for row in rows[1:]] |  |  |  |
|     return "\\n".join([header |  separator |  *body]) + "\\n" |  |
|  |  |  |  |
|  |  |  |  |
| def main(): |  |  |  |
|     parser = argparse.ArgumentParser(description="Render a CSV file or CSV text as a Markdown table.") |  |  |  |
|     parser.add_argument("input" |  help="CSV file path |  CSV text |  or '-' to read CSV text from stdin") |
|     parser.add_argument("-o" |  "--output" |  help="Markdown output path (default: <input-name>.md or output.md)") |  |
|     args = parser.parse_args() |  |  |  |
|  |  |  |  |
|     input_path = Path(args.input) |  |  |  |
|     if args.input == "-": |  |  |  |
|         csv_text = sys.stdin.read() |  |  |  |
|         default_output = Path("output.md") |  |  |  |
|     elif input_path.is_file(): |  |  |  |
|         csv_text = input_path.read_text(encoding="utf-8-sig") |  |  |  |
|         default_output = input_path.with_suffix(".md") |  |  |  |
|     else: |  |  |  |
|         csv_text = args.input |  |  |  |
|         default_output = Path("output.md") |  |  |  |
|  |  |  |  |
|     try: |  |  |  |
|         markdown = csv_to_markdown(csv_text) |  |  |  |
|     except ValueError as error: |  |  |  |
|         print(f"Input rejected: {error}" |  file=sys.stderr) |  |  |
|         return 2 |  |  |  |
|  |  |  |  |
|     output_path = Path(args.output) if args.output else default_output |  |  |  |
|     output_path.write_text(markdown |  encoding="utf-8") |  |  |
|     return 0 |  |  |  |
|  |  |  |  |
|  |  |  |  |
| if __name__ == "__main__": |  |  |  |
|     sys.exit(main()) |  |  |  |
