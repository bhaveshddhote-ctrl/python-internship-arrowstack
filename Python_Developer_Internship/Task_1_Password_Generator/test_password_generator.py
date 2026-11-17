"""
Comprehensive Automated Test Suite for Task 1: Password Generator
Verifies normal inputs, invalid inputs, boundary cases, category guarantees,
and security requirements.
"""

import sys
import unittest
import string
import importlib.util

# Load password_generator module dynamically
spec = importlib.util.spec_from_file_location(
    "password_generator",
    "Python_Developer_Internship/Task_1_Password_Generator/password_generator.py"
)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


class TestPasswordGenerator(unittest.TestCase):

    def test_default_generation_length(self):
        """Test password length matches requested length."""
        for length in [8, 12, 16, 32, 64]:
            pwd = pg.generate_single_password(length)
            self.assertEqual(len(pwd), length, f"Password length must be {length}")

    def test_guaranteed_category_inclusion_all(self):
        """Test that every enabled category has at least one character present."""
        for _ in range(50):  # Run 50 iterations to ensure consistency
            pwd = pg.generate_single_password(
                length=16,
                use_upper=True,
                use_lower=True,
                use_digits=True,
                use_symbols=True,
            )
            has_upper = any(c in pg.UPPERCASE_CHARS for c in pwd)
            has_lower = any(c in pg.LOWERCASE_CHARS for c in pwd)
            has_digit = any(c in pg.DIGIT_CHARS for c in pwd)
            has_symbol = any(c in pg.SYMBOL_CHARS for c in pwd)

            self.assertTrue(has_upper, "Must contain at least one uppercase letter.")
            self.assertTrue(has_lower, "Must contain at least one lowercase letter.")
            self.assertTrue(has_digit, "Must contain at least one digit.")
            self.assertTrue(has_symbol, "Must contain at least one special symbol.")

    def test_boundary_case_minimum_length(self):
        """Boundary test: length exactly equals number of enabled categories."""
        # 4 categories enabled, length = 4
        pwd = pg.generate_single_password(4, use_upper=True, use_lower=True, use_digits=True, use_symbols=True)
        self.assertEqual(len(pwd), 4)
        self.assertTrue(any(c in pg.UPPERCASE_CHARS for c in pwd))
        self.assertTrue(any(c in pg.LOWERCASE_CHARS for c in pwd))
        self.assertTrue(any(c in pg.DIGIT_CHARS for c in pwd))
        self.assertTrue(any(c in pg.SYMBOL_CHARS for c in pwd))

    def test_disabled_categories_are_strictly_excluded(self):
        """Test that disabled categories NEVER appear in the generated password."""
        # Only lowercase and digits
        for _ in range(25):
            pwd = pg.generate_single_password(
                length=20,
                use_upper=False,
                use_lower=True,
                use_digits=True,
                use_symbols=False,
            )
            self.assertFalse(any(c in pg.UPPERCASE_CHARS for c in pwd), "Uppercase must NOT be present.")
            self.assertFalse(any(c in pg.SYMBOL_CHARS for c in pwd), "Symbols must NOT be present.")
            self.assertTrue(any(c in pg.LOWERCASE_CHARS for c in pwd), "Lowercase must be present.")
            self.assertTrue(any(c in pg.DIGIT_CHARS for c in pwd), "Digits must be present.")

    def test_single_category_only(self):
        """Test password generation when only one category is chosen."""
        pwd_digits = pg.generate_single_password(10, use_upper=False, use_lower=False, use_digits=True, use_symbols=False)
        self.assertTrue(pwd_digits.isdigit())
        self.assertEqual(len(pwd_digits), 10)

    def test_length_less_than_categories_raises_value_error(self):
        """Test that requesting length < enabled categories raises ValueError."""
        with self.assertRaises(ValueError):
            # 4 categories enabled but length requested is 3
            pg.generate_single_password(3, use_upper=True, use_lower=True, use_digits=True, use_symbols=True)

    def test_no_categories_selected_raises_value_error(self):
        """Test that calling generator with no categories raises ValueError."""
        with self.assertRaises(ValueError):
            pg.generate_single_password(12, use_upper=False, use_lower=False, use_digits=False, use_symbols=False)

    def test_generate_multiple_passwords(self):
        """Test multiple passwords batch generation."""
        prefs = {"upper": True, "lower": True, "digits": True, "symbols": True}
        passwords = pg.generate_multiple_passwords(count=5, length=14, prefs=prefs)
        self.assertEqual(len(passwords), 5)
        for pwd in passwords:
            self.assertEqual(len(pwd), 14)
        # Passwords should be unique
        self.assertEqual(len(set(passwords)), 5, "Generated passwords should all be distinct")


if __name__ == "__main__":
    unittest.main()
