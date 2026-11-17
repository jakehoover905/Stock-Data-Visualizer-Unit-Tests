
import unittest
from unittest.mock import patch

import main as app


def run_input(func, answers, *args):
    """Call an input function with fake user answers, silencing print()."""
    with patch("builtins.input", side_effect=answers), patch("builtins.print"):
        return func(*args)


# 1. Symbol: capitalized, 1-7 alpha characters
class TestSymbol(unittest.TestCase):
    GOOD = "AAPL"

    def test_valid_symbols(self):
        for symbol in ["A", "AAPL", "MSFT", "GOOGLEX"]:  # 1, 4, 4, 7 letters
            with self.subTest(symbol=symbol):
                self.assertEqual(run_input(app.get_symbol, [symbol]), symbol)

    def test_lowercase_is_capitalized(self):
        self.assertEqual(run_input(app.get_symbol, ["aapl"]), "AAPL")

    def test_mixed_case_is_capitalized(self):
        self.assertEqual(run_input(app.get_symbol, ["aApL"]), "AAPL")

    def test_surrounding_whitespace_is_stripped(self):
        self.assertEqual(run_input(app.get_symbol, ["  aapl  "]), "AAPL")

    def test_invalid_symbols_are_rejected(self):
        bad_values = {
            "empty": "",
            "only spaces": "   ",
            "8 characters (too long)": "ABCDEFGH",
            "contains digit": "AAPL1",
            "all digits": "1234",
            "contains period": "BRK.B",
            "contains hyphen": "BRK-B",
            "contains space": "AA PL",
            "special characters": "AA$L",
            "non-ASCII letter": "AAPÉ",
        }
        for label, bad in bad_values.items():
            with self.subTest(case=label):
                self.assertEqual(run_input(app.get_symbol, [bad, self.GOOD]), self.GOOD)


# 2. Chart type: 1 numeric character, 1 or 2
class TestChartType(unittest.TestCase):
    PROMPT = "Enter the chart type you want (1, 2): "

    def ask(self, answers):
        return run_input(app.get_menu_choice, answers, self.PROMPT, app.Chart_Types)

    def test_valid_choices(self):
        for choice in ["1", "2"]:
            with self.subTest(choice=choice):
                self.assertEqual(self.ask([choice]), choice)

    def test_choices_map_to_chart_names(self):
        self.assertEqual(app.Chart_Types[self.ask(["1"])], "bar")
        self.assertEqual(app.Chart_Types[self.ask(["2"])], "line")

    def test_invalid_choices_are_rejected(self):
        for bad in ["0", "3", "9", "12", "-1", "1.0", "a", "bar", "", " "]:
            with self.subTest(choice=bad):
                self.assertEqual(self.ask([bad, "1"]), "1")


# 3. Time series: 1 numeric character, 1 - 4
class TestTimeSeries(unittest.TestCase):
    PROMPT = "Enter the time series option (1, 2, 3, 4): "

    def ask(self, answers):
        return run_input(app.get_menu_choice, answers, self.PROMPT, app.Time_Series)

    def test_valid_choices(self):
        for choice in ["1", "2", "3", "4"]:
            with self.subTest(choice=choice):
                self.assertEqual(self.ask([choice]), choice)

    def test_choices_map_to_alpha_vantage_functions(self):
        expected = {
            "1": "TIME_SERIES_INTRADAY",
            "2": "TIME_SERIES_DAILY",
            "3": "TIME_SERIES_WEEKLY",
            "4": "TIME_SERIES_MONTHLY",
        }
        for choice, function in expected.items():
            with self.subTest(choice=choice):
                self.assertEqual(app.Time_Series[self.ask([choice])], function)

    def test_invalid_choices_are_rejected(self):
        for bad in ["0", "5", "9", "10", "12", "-1", "2.5", "a", "daily", "", " "]:
            with self.subTest(choice=bad):
                self.assertEqual(self.ask([bad, "2"]), "2")


# 4. Start date: date type YYYY-MM-DD
class TestStartDate(unittest.TestCase):
    PROMPT = "Enter the start date (YYYY-MM-DD): "
    GOOD = "2024-01-31"

    def ask(self, answers):
        return run_input(app.get_date, answers, self.PROMPT)

    def test_valid_dates(self):
        for text in ["2024-01-31", "1999-12-31", "2000-01-01", "2024-02-29"]:  # leap day
            with self.subTest(date=text):
                self.assertEqual(self.ask([text]), text)

    def test_whitespace_is_stripped(self):
        self.assertEqual(self.ask(["  2024-01-31  "]), "2024-01-31")

    def test_invalid_dates_are_rejected(self):
        bad_values = {
            "empty": "",
            "text": "abc",
            "wrong order (MM-DD-YYYY)": "01-31-2024",
            "wrong order (DD-MM-YYYY)": "31-01-2024",
            "slashes": "2024/01/31",
            "no separators": "20240131",
            "no zero padding": "2024-1-5",
            "month 13": "2024-13-01",
            "month 00": "2024-00-10",
            "day 32": "2024-01-32",
            "day 00": "2024-01-00",
            "Feb 29 on a non-leap year": "2023-02-29",
            "April 31": "2024-04-31",
            "ISO week format": "2024-W01-1",
            "date with time": "2024-01-31 10:30",
            "two-digit year": "24-01-31",
        }
        for label, bad in bad_values.items():
            with self.subTest(case=label):
                self.assertEqual(self.ask([bad, self.GOOD]), self.GOOD)


# 5. End date: date type YYYY-MM-DD (and not before the start date)
class TestEndDate(unittest.TestCase):
    START = "2024-01-31"
    GOOD = "2024-02-15"

    def ask(self, answers, start=None):
        return run_input(app.get_end_date, answers, start or self.START)

    def test_valid_end_dates(self):
        for text in ["2024-02-15", "2025-01-01", "2024-02-29"]:
            with self.subTest(date=text):
                self.assertEqual(self.ask([text]), text)

    def test_end_date_may_equal_start_date(self):
        self.assertEqual(self.ask([self.START]), self.START)

    def test_end_date_before_start_is_rejected(self):
        for early in ["2024-01-30", "2023-12-31", "1999-01-01"]:
            with self.subTest(date=early):
                self.assertEqual(self.ask([early, self.GOOD]), self.GOOD)

    def test_invalid_formats_are_rejected(self):
        bad_values = {
            "empty": "",
            "text": "abc",
            "wrong order": "02-15-2024",
            "slashes": "2024/02/15",
            "no separators": "20240215",
            "no zero padding": "2024-2-5",
            "month 13": "2024-13-01",
            "day 32": "2024-02-32",
            "Feb 29 on a non-leap year": "2023-02-29",
            "ISO week format": "2024-W07-4",
        }
        for label, bad in bad_values.items():
            with self.subTest(case=label):
                self.assertEqual(self.ask([bad, self.GOOD]), self.GOOD)

    def test_multiple_bad_attempts_then_good(self):
        self.assertEqual(self.ask(["nope", "2020-01-01", "2024-99-99", self.GOOD]), self.GOOD)


if __name__ == "__main__":
    unittest.main()
