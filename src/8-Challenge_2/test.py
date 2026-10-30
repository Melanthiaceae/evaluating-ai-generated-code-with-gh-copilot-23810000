import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import solution


class ParseCsvTests(unittest.TestCase):
    def test_parses_quoted_commas_quotes_and_empty_fields(self):
        rows = solution.parse_csv('name,note,empty\nAda,"likes, commas",""\n')

        self.assertEqual(rows, [["name", "note", "empty"], ["Ada", "likes, commas", ""]])

    def test_parses_newlines_inside_quoted_fields(self):
        rows = solution.parse_csv('name,note\nAda,"first line\nsecond line"\n')

        self.assertEqual(rows, [["name", "note"], ["Ada", "first line\nsecond line"]])

    def test_preserves_missing_fields(self):
        rows = solution.parse_csv("a,b,c\n1,2\n")

        self.assertEqual(rows, [["a", "b", "c"], ["1", "2"]])

    def test_rejects_empty_or_non_comma_separated_input(self):
        for text in ("", "   ", "one column\nanother"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                solution.parse_csv(text)

    def test_rejects_malformed_quoted_fields(self):
        with self.assertRaisesRegex(ValueError, "CSV parsing failed"):
            solution.parse_csv('name,note\nAda,"unclosed\n')


class CsvToMarkdownTests(unittest.TestCase):
    def test_formats_rows_and_escapes_markdown_content(self):
        markdown = solution.csv_to_markdown('name,note\nAda,"a|b"\n')

        self.assertEqual(markdown, "| name | note |\n| --- | --- |\n| Ada | a\\|b |\n")

    def test_formats_newlines_and_pads_short_rows(self):
        markdown = solution.csv_to_markdown('a,b,c\n"first\nsecond",value\n')

        self.assertEqual(
            markdown,
            "| a | b | c |\n| --- | --- | --- |\n| first<br>second | value |  |\n",
        )


class CsvToTableTests(unittest.TestCase):
    def test_formats_aligned_plain_text_table(self):
        table = solution.csv_to_table("name,note\nAda,ok\n")

        self.assertEqual(
            table,
            "+------+------+\n"
            "| name | note |\n"
            "+------+------+\n"
            "| Ada  | ok   |\n"
            "+------+------+\n",
        )

    def test_replaces_newlines_and_pads_short_rows(self):
        table = solution.csv_to_table('a,b,c\n"first\nsecond",value\n')

        self.assertIn("first / second", table)
        self.assertIn("| value |", table)
        self.assertTrue(table.endswith("+----------------+-------+---+\n"))

    def test_aligns_wide_unicode_and_escapes_tabs(self):
        table = solution.csv_to_table("name,note\n東京,a\tb\nA,ok\n")

        self.assertEqual(
            table,
            "+------+------+\n"
            "| name | note |\n"
            "+------+------+\n"
            "| 東京 | a\\tb |\n"
            "| A    | ok   |\n"
            "+------+------+\n",
        )


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.script = Path(__file__).with_name("solution.py")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_solution(self, *args, input_text=None):
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=self.directory,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_rejects_existing_non_csv_file(self):
        input_file = self.directory / "data.txt"
        input_file.write_text("a,b\n1,2\n", encoding="utf-8")

        result = self.run_solution(str(input_file))

        self.assertEqual(result.returncode, 2)
        self.assertIn("must have a .csv extension", result.stderr)
        self.assertFalse((self.directory / "data.md").exists())

    def test_rejects_missing_csv_file(self):
        input_file = self.directory / "missing.csv"

        result = self.run_solution(str(input_file))

        self.assertEqual(result.returncode, 2)
        self.assertIn("missing file", result.stderr)
        self.assertIn(str(input_file), result.stderr)
        self.assertFalse((self.directory / "output.md").exists())

    def test_accepts_csv_extension_case_insensitively(self):
        input_file = self.directory / "data.CSV"
        input_file.write_text("a,b\n1,2\n", encoding="utf-8")

        result = self.run_solution(str(input_file))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.directory / "data.md").read_text(encoding="utf-8"),
            "| a | b |\n| --- | --- |\n| 1 | 2 |\n",
        )

    def test_accepts_csv_text(self):
        output_file = self.directory / "text.md"

        result = self.run_solution("a,b\n1,2", "-o", str(output_file))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output_file.exists())

    def test_output_option_always_uses_markdown_extension(self):
        test_cases = (
            ("report", "report.md"),
            ("already.md", "already.md"),
            ("report.txt", "report.txt.md"),
            ("uppercase.MD", "uppercase.MD"),
        )
        for output_name, expected_name in test_cases:
            with self.subTest(output_name=output_name):
                result = self.run_solution("a,b\n1,2", "-o", output_name)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((self.directory / expected_name).exists())
                self.assertEqual(
                    (self.directory / expected_name).read_text(encoding="utf-8"),
                    "| a | b |\n| --- | --- |\n| 1 | 2 |\n",
                )

    def test_accepts_csv_from_stdin(self):
        output_file = self.directory / "stdin.md"

        result = self.run_solution("-", "-o", str(output_file), input_text="a,b\n1,2\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output_file.exists())

    def test_cli_mode_prints_table_without_creating_markdown(self):
        input_file = self.directory / "data.csv"
        input_file.write_text("a,b\n1,2\n", encoding="utf-8")

        result = self.run_solution(str(input_file), "-cli")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "+---+---+\n| a | b |\n+---+---+\n| 1 | 2 |\n+---+---+\n",
        )
        self.assertFalse((self.directory / "data.md").exists())

    def test_cli_mode_rejects_output_file_option(self):
        result = self.run_solution("a,b\n1,2", "-cli", "-o", "table.md")

        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot be used with -cli", result.stderr)
        self.assertFalse((self.directory / "table.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
