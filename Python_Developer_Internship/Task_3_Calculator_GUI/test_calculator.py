"""
Comprehensive Automated Test Suite for Task 3: Calculator with GUI
Verifies:
- Core arithmetic operations (+, -, *, /, %)
- Floating-point calculations and precision
- Operator precedence
- Division by zero handling
- AST security engine (blocks arbitrary code execution)
- GUI state logic (digit entry, duplicate decimal prevention, backspace, clear, sign toggle, equals)
- Window opening and destruction without crashing
"""

import sys
import unittest
import importlib.util
import tkinter as tk

# Dynamically import calculator main module
spec = importlib.util.spec_from_file_location(
    "calc_main",
    "Python_Developer_Internship/Task_3_Calculator_GUI/main.py"
)
calc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calc)


class TestSafeCalculationEngine(unittest.TestCase):
    """Test the safe AST-based arithmetic evaluation engine."""

    def test_basic_addition(self):
        self.assertEqual(calc.calculate_expression("15 + 25"), "40")

    def test_basic_subtraction(self):
        self.assertEqual(calc.calculate_expression("50 − 18"), "32")
        self.assertEqual(calc.calculate_expression("10 - 25"), "-15")

    def test_basic_multiplication(self):
        self.assertEqual(calc.calculate_expression("7 × 8"), "56")

    def test_basic_division(self):
        self.assertEqual(calc.calculate_expression("100 ÷ 4"), "25")
        self.assertEqual(calc.calculate_expression("7 ÷ 2"), "3.5")

    def test_decimal_calculations(self):
        self.assertEqual(calc.calculate_expression("12.5 + 7.25"), "19.75")
        self.assertEqual(calc.calculate_expression("0.1 + 0.2"), "0.3")

    def test_operator_precedence(self):
        # 4 + (5 * 2) = 14
        self.assertEqual(calc.calculate_expression("4 + 5 × 2"), "14")
        # (20 / 4) - 2 = 3
        self.assertEqual(calc.calculate_expression("20 ÷ 4 − 2"), "3")

    def test_division_by_zero_raises_error(self):
        with self.assertRaises(ZeroDivisionError):
            calc.calculate_expression("42 ÷ 0")

    def test_ast_security_blocks_code_injection(self):
        """Security Test: ensure arbitrary Python code is strictly blocked."""
        malicious_inputs = [
            "__import__('os').system('dir')",
            "open('passwords.txt', 'r')",
            "eval('2+2')",
            "print('hack')",
            "lambda x: x",
        ]
        for attack in malicious_inputs:
            with self.assertRaises(ValueError):
                calc.calculate_expression(attack)


class TestCalculatorGUIState(unittest.TestCase):
    """Test GUI interactions and state machine headlessly."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during automated test
        self.app = calc.CalculatorApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initial_state(self):
        self.assertEqual(self.app.display_var.get(), "0")
        self.assertEqual(self.app.history_var.get(), "")

    def test_digit_entry(self):
        self.app._handle_button_press("1")
        self.app._handle_button_press("2")
        self.app._handle_button_press("3")
        self.assertEqual(self.app.display_var.get(), "123")

    def test_decimal_entry_and_duplicate_prevention(self):
        self.app._handle_button_press("5")
        self.app._handle_button_press(".")
        self.app._handle_button_press("2")
        self.assertEqual(self.app.display_var.get(), "5.2")

        # Pressing decimal again should be ignored
        self.app._handle_button_press(".")
        self.assertEqual(self.app.display_var.get(), "5.2")

    def test_backspace(self):
        self.app._handle_button_press("9")
        self.app._handle_button_press("8")
        self.assertEqual(self.app.display_var.get(), "98")
        self.app._handle_button_press("⌫")
        self.assertEqual(self.app.display_var.get(), "9")
        self.app._handle_button_press("⌫")
        self.assertEqual(self.app.display_var.get(), "0")

    def test_clear_button(self):
        self.app._handle_button_press("9")
        self.app._handle_button_press("+")
        self.app._handle_button_press("5")
        self.app._handle_button_press("C")
        self.assertEqual(self.app.display_var.get(), "0")
        self.assertEqual(self.app.history_var.get(), "")

    def test_sign_toggle(self):
        self.app._handle_button_press("4")
        self.app._handle_button_press("2")
        self.app._handle_button_press("±")
        self.assertEqual(self.app.display_var.get(), "-42")
        self.app._handle_button_press("±")
        self.assertEqual(self.app.display_var.get(), "42")

    def test_operator_replacement(self):
        self.app._handle_button_press("8")
        self.app._handle_button_press("+")
        # Change mind, press multiply instead
        self.app._handle_button_press("×")
        self.assertEqual(self.app.display_var.get(), "8 × ")

    def test_complete_calculation_flow(self):
        # 15 + 25 = 40
        self.app._handle_button_press("1")
        self.app._handle_button_press("5")
        self.app._handle_button_press("+")
        self.app._handle_button_press("2")
        self.app._handle_button_press("5")
        self.app._handle_button_press("=")
        self.assertEqual(self.app.display_var.get(), "40")
        self.assertEqual(self.app.history_var.get(), "15 + 25 =")

    def test_division_by_zero_in_gui(self):
        # 9 ÷ 0 = Cannot divide by zero
        self.app._handle_button_press("9")
        self.app._handle_button_press("÷")
        self.app._handle_button_press("0")
        self.app._handle_button_press("=")
        self.assertEqual(self.app.display_var.get(), "Cannot divide by zero")


if __name__ == "__main__":
    unittest.main()
