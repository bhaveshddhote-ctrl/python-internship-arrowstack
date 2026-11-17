"""
Task 3: Calculator with GUI
Internship Project: Auspify Technologies Python Developer Internship
Description: A professional, secure, and modern desktop calculator application.
Built using Python 3 and Tkinter with a safe AST-based arithmetic evaluation engine.
Follows PEP 8 guidelines and strictly uses Python's standard library.
"""

import ast
import operator
import sys
import tkinter as tk
from tkinter import font as tkfont


# ---------------------------------------------------------------------------
# Safe Arithmetic Evaluation Engine (Zero eval() vulnerability)
# ---------------------------------------------------------------------------

# Supported safe arithmetic operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval_node(node):
    """Recursively evaluate an AST node strictly restricted to basic arithmetic.

    Raises:
        ZeroDivisionError: When division or modulo by zero occurs.
        ValueError: When unsafe syntax, functions, or variables are detected.
    """
    if isinstance(node, ast.Expression):
        return safe_eval_node(node.body)

    if isinstance(node, ast.Constant):  # Python 3.8+ numeric constant
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    if isinstance(node, ast.BinOp):
        left_val = safe_eval_node(node.left)
        right_val = safe_eval_node(node.right)
        op_type = type(node.op)

        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")

        if op_type in (ast.Div, ast.Mod) and right_val == 0:
            raise ZeroDivisionError("Cannot divide by zero")

        return SAFE_OPERATORS[op_type](left_val, right_val)

    if isinstance(node, ast.UnaryOp):
        operand_val = safe_eval_node(node.operand)
        op_type = type(node.op)

        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

        return SAFE_OPERATORS[op_type](operand_val)

    raise ValueError(f"Unsafe or forbidden expression syntax: {type(node).__name__}")


def calculate_expression(expr_str: str) -> str:
    """Safely calculate the result of an arithmetic string expression.

    Returns:
        Formatted string of the result (e.g. '42' or '3.1415'),
        or raises ZeroDivisionError/ValueError on error.
    """
    # Clean up display symbols into standard Python arithmetic operators
    sanitized = (
        expr_str.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .strip()
    )

    if not sanitized:
        return "0"

    try:
        parsed_ast = ast.parse(sanitized, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid Format")

    raw_result = safe_eval_node(parsed_ast)

    # Format result: remove unnecessary trailing .0 and round floating-point inaccuracies
    if isinstance(raw_result, float):
        if raw_result.is_integer():
            return str(int(raw_result))
        # Round to 10 decimal places to eliminate floating-point artifacts like 0.30000000000000004
        rounded = round(raw_result, 10)
        return f"{rounded:g}"

    return str(raw_result)


# ---------------------------------------------------------------------------
# Graphical User Interface (Tkinter)
# ---------------------------------------------------------------------------

# Color Palette (Modern Dark Slate Theme)
THEME = {
    "bg_main": "#1e1e2e",       # App window background
    "bg_display": "#181825",    # Display screen background
    "txt_primary": "#cdd6f4",   # Main numbers text (White)
    "txt_secondary": "#a6adc8", # History/expression text (Soft Gray)
    "txt_accent": "#89b4fa",    # Accent text (Sky Blue)
    "btn_num": "#313244",       # Number button background
    "btn_num_hover": "#45475a", # Number button hover
    "btn_op": "#45475a",        # Operator button background
    "btn_op_hover": "#585b70",  # Operator button hover
    "btn_clear": "#f38ba8",     # Clear/Delete button background (Soft Coral)
    "btn_clear_fg": "#11111b",  # Clear text color
    "btn_eq": "#a6e3a1",        # Equals button background (Emerald Green)
    "btn_eq_fg": "#11111b",     # Equals text color
}


class CalculatorApp:
    """Professional desktop calculator with Tkinter."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator Pro")
        self.root.geometry("360x520")
        self.root.minsize(320, 460)
        self.root.configure(bg=THEME["bg_main"])

        # State Variables
        self.current_entry = "0"
        self.history_expr = ""
        self.result_just_calculated = False

        # Build Interface
        self._setup_display()
        self._setup_buttons()
        self._setup_keyboard_bindings()

    def _setup_display(self):
        """Create the modern dual-line display area."""
        display_frame = tk.Frame(self.root, bg=THEME["bg_display"], padx=15, pady=12)
        display_frame.pack(fill="x", padx=14, pady=(14, 8))

        # Top line: shows history expression (e.g., '12 + 5 =')
        self.history_var = tk.StringVar(value="")
        self.history_label = tk.Label(
            display_frame,
            textvariable=self.history_var,
            font=("Segoe UI", 12),
            fg=THEME["txt_secondary"],
            bg=THEME["bg_display"],
            anchor="e",
        )
        self.history_label.pack(fill="x")

        # Bottom line: shows active input or result
        self.display_var = tk.StringVar(value="0")
        self.display_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=("Segoe UI", 28, "bold"),
            fg=THEME["txt_primary"],
            bg=THEME["bg_display"],
            anchor="e",
        )
        self.display_label.pack(fill="x", pady=(2, 0))

    def _setup_buttons(self):
        """Create grid of calculator buttons with styling and hover effects."""
        buttons_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        buttons_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Configure 4 columns and 5 rows with equal weight
        for col in range(4):
            buttons_frame.columnconfigure(col, weight=1)
        for row in range(5):
            buttons_frame.rowconfigure(row, weight=1)

        # Button Layout Grid: (Label, Row, Col, Type)
        button_specs = [
            ("C", 0, 0, "clear"),
            ("⌫", 0, 1, "backspace"),
            ("%", 0, 2, "op"),
            ("÷", 0, 3, "op"),

            ("7", 1, 0, "num"),
            ("8", 1, 1, "num"),
            ("9", 1, 2, "num"),
            ("×", 1, 3, "op"),

            ("4", 2, 0, "num"),
            ("5", 2, 1, "num"),
            ("6", 2, 2, "num"),
            ("−", 2, 3, "op"),

            ("1", 3, 0, "num"),
            ("2", 3, 1, "num"),
            ("3", 3, 2, "num"),
            ("+", 3, 3, "op"),

            ("±", 4, 0, "num"),
            ("0", 4, 1, "num"),
            (".", 4, 2, "num"),
            ("=", 4, 3, "eq"),
        ]

        for text, r, c, b_type in button_specs:
            self._create_button(buttons_frame, text, r, c, b_type)

    def _create_button(self, parent, text, row, col, b_type):
        """Create an individual button with styling according to its role."""
        if b_type == "clear":
            bg = THEME["btn_clear"]
            fg = THEME["btn_clear_fg"]
            active_bg = "#f5c2e7"
        elif b_type == "eq":
            bg = THEME["btn_eq"]
            fg = THEME["btn_eq_fg"]
            active_bg = "#94e2d5"
        elif b_type == "op":
            bg = THEME["btn_op"]
            fg = THEME["txt_accent"]
            active_bg = THEME["btn_op_hover"]
        else:  # 'num' or 'backspace'
            bg = THEME["btn_num"]
            fg = THEME["txt_primary"]
            active_bg = THEME["btn_num_hover"]

        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 16, "bold"),
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda t=text: self._handle_button_press(t),
        )
        btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

    def _setup_keyboard_bindings(self):
        """Bind physical keyboard keys for intuitive input."""
        self.root.bind("<Key>", self._handle_key_event)

    def _handle_key_event(self, event):
        """Process keyboard inputs."""
        char = event.char
        keysym = event.keysym

        if char in "0123456789.":
            self._handle_button_press(char)
        elif char == "+":
            self._handle_button_press("+")
        elif char == "-":
            self._handle_button_press("−")
        elif char == "*":
            self._handle_button_press("×")
        elif char == "/":
            self._handle_button_press("÷")
        elif char == "%":
            self._handle_button_press("%")
        elif keysym in ("Return", "KP_Enter") or char == "=":
            self._handle_button_press("=")
        elif keysym == "BackSpace":
            self._handle_button_press("⌫")
        elif keysym == "Escape" or char.lower() == "c":
            self._handle_button_press("C")

    # -----------------------------------------------------------------------
    # Business Logic & Button Handlers
    # -----------------------------------------------------------------------

    def _handle_button_press(self, token: str):
        """Central controller for all calculator button and key actions."""
        if token == "C":
            self._action_clear()
        elif token == "⌫":
            self._action_backspace()
        elif token == "=":
            self._action_equals()
        elif token == "±":
            self._action_toggle_sign()
        elif token in ("+", "−", "×", "÷", "%"):
            self._action_operator(token)
        elif token == ".":
            self._action_decimal()
        else:
            self._action_digit(token)

    def _action_clear(self):
        """Clear all inputs and reset display state."""
        self.current_entry = "0"
        self.history_expr = ""
        self.result_just_calculated = False
        self._update_display()

    def _action_backspace(self):
        """Delete the most recent character or reset to 0."""
        if self.result_just_calculated:
            # If user presses backspace right after calculation, clear history
            self.history_expr = ""
            self.result_just_calculated = False

        if len(self.current_entry) > 1:
            self.current_entry = self.current_entry[:-1]
        else:
            self.current_entry = "0"
        self._update_display()

    def _action_digit(self, digit: str):
        """Append digit to current entry."""
        if self.result_just_calculated:
            # Fresh start after an equals operation
            self.current_entry = digit
            self.history_expr = ""
            self.result_just_calculated = False
        else:
            if self.current_entry == "0":
                self.current_entry = digit
            else:
                self.current_entry += digit
        self._update_display()

    def _action_decimal(self):
        """Insert decimal point ensuring no duplicates in active number."""
        if self.result_just_calculated:
            self.current_entry = "0."
            self.history_expr = ""
            self.result_just_calculated = False
        else:
            # Prevent multiple dots in a single number token
            tokens = self.current_entry.split()
            last_token = tokens[-1] if tokens else ""
            if "." not in last_token:
                self.current_entry += "."
        self._update_display()

    def _action_toggle_sign(self):
        """Negate the current number entry."""
        if self.current_entry == "0" or self.current_entry in ("Cannot divide by zero", "Invalid Format"):
            return

        try:
            val = float(self.current_entry)
            if val.is_integer():
                self.current_entry = str(int(-val))
            else:
                self.current_entry = f"{-val:g}"
            self._update_display()
        except ValueError:
            # If current_entry has multiple terms, toggle sign of whole block
            if self.current_entry.startswith("-"):
                self.current_entry = self.current_entry[1:]
            else:
                self.current_entry = "-" + self.current_entry
            self._update_display()

    def _action_operator(self, op: str):
        """Append an operator, chaining operations smoothly."""
        if self.current_entry in ("Cannot divide by zero", "Invalid Format"):
            self._action_clear()

        # If previous character is already an operator, replace it
        if self.current_entry.endswith((" + ", " − ", " × ", " ÷ ", " % ")):
            self.current_entry = self.current_entry[:-3] + f" {op} "
        else:
            self.current_entry += f" {op} "

        self.result_just_calculated = False
        self._update_display()

    def _action_equals(self):
        """Evaluate the full expression safely and display result."""
        if not self.current_entry:
            return

        # Strip trailing dangling operators (e.g. '5 +')
        expr = self.current_entry.strip()
        while expr.endswith(("+", "−", "×", "÷", "%", "-", "*", "/")):
            expr = expr[:-1].strip()

        if not expr:
            return

        try:
            result = calculate_expression(expr)
            self.history_expr = f"{self.current_entry} ="
            self.current_entry = result
            self.result_just_calculated = True
        except ZeroDivisionError:
            self.history_expr = f"{self.current_entry} ="
            self.current_entry = "Cannot divide by zero"
            self.result_just_calculated = True
        except (ValueError, Exception):
            self.history_expr = f"{self.current_entry} ="
            self.current_entry = "Invalid Format"
            self.result_just_calculated = True

        self._update_display()

    def _update_display(self):
        """Refresh the Tkinter UI labels with current state."""
        self.history_var.set(self.history_expr)
        self.display_var.set(self.current_entry)


# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------

def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
