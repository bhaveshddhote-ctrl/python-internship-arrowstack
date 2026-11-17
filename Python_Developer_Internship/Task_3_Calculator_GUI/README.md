# Task 3: Calculator with GUI (Tkinter)

A professional, modern, and cryptographically secure desktop calculator application built using Python 3 and Tkinter.

Developed as part of the **Auspify Technologies Python Developer Internship**.

---

## 📌 Project Overview

This desktop calculator application combines an intuitive, modern dark-slate user interface with a **zero-vulnerability AST-based arithmetic engine**. Unlike naive implementations that use dangerous `eval()` functions, this application parses and evaluates arithmetic expressions securely without exposing the host operating system to arbitrary code execution attacks.

---

## ✨ Features

- **Modern Dark-Slate UI**:
  - Dual-line display: Small top history label (e.g., `15 + 25 =`) and large bottom main result display.
  - Distinct color-coded buttons: Digits in neutral dark slate, operators in accented colors, equals in emerald green, and clear/backspace in soft coral/peach.
- **Full Arithmetic Support**:
  - Addition (`+`), Subtraction (`−`), Multiplication (`×`), Division (`÷`), and Modulo (`%`).
  - Negation / Sign Toggle (`±`).
  - Full decimal point support with duplicate dot prevention.
- **Zero-Vulnerability Safe Evaluation**:
  - Replaces unsafe `eval()` with an **Abstract Syntax Tree (AST)** evaluator using Python's standard `ast` module.
  - Strictly restricts execution to standard numeric constants and safe binary/unary operators.
- **Graceful Error Handling**:
  - Catches `ZeroDivisionError` cleanly and displays `"Cannot divide by zero"` without crashing.
  - Automatically resets state on subsequent input.
- **Physical Keyboard Support**:
  - Full keyboard bindings for digits `0–9`, operators `+`, `-`, `*`, `/`, `%`, `Enter` or `=` for calculate, `Backspace` for delete, and `Escape` or `c` for clear.
- **Zero External Dependencies**: Built 100% on Python's built-in `tkinter` and `ast` libraries.

---

## 🛠️ Prerequisites

- **Python**: Version 3.8 or higher (Tested on Python 3.14)
- **Tkinter**: Included in standard Python distributions for Windows/macOS.
- **External Packages**: None required.

---

## 🚀 How to Run the Application

Open your terminal or PowerShell in the root directory and execute:

```bash
python Python_Developer_Internship/Task_3_Calculator_GUI/main.py
```

A clean desktop calculator window will appear on your screen ready for interaction via mouse clicks or your keyboard!

---

## ⌨️ Keyboard Shortcuts Reference

| Key | Calculator Action |
| :--- | :--- |
| `0` – `9` | Input Digits |
| `.` | Input Decimal Point (Single per number) |
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |
| `Enter` or `=` | Calculate Result (Equals) |
| `Backspace` | Delete last entered character |
| `Escape` or `c` / `C` | Clear All (`C`) |

---

## 🧪 Automated Testing & Verification

The project includes 17 automated unit tests in `test_calculator.py` verifying all math operations, operator precedence, decimal calculations, GUI state transitions, and AST security isolation.

Run the test suite with:

```bash
python Python_Developer_Internship/Task_3_Calculator_GUI/test_calculator.py -v
```

### Verified Test Results:

```text
test_backspace ... ok
test_clear_button ... ok
test_complete_calculation_flow ... ok
test_decimal_entry_and_duplicate_prevention ... ok
test_digit_entry ... ok
test_division_by_zero_in_gui ... ok
test_initial_state ... ok
test_operator_replacement ... ok
test_sign_toggle ... ok
test_ast_security_blocks_code_injection ... ok
test_basic_addition ... ok
test_basic_division ... ok
test_basic_multiplication ... ok
test_basic_subtraction ... ok
test_decimal_calculations ... ok
test_division_by_zero_raises_error ... ok
test_operator_precedence ... ok

----------------------------------------------------------------------
Ran 17 tests in 2.334s

OK
```

---

## 📁 Project Structure

```text
Python_Developer_Internship/
├── Task_1_Password_Generator/
├── Task_2_Todo_List/
└── Task_3_Calculator_GUI/
    ├── main.py              # Tkinter GUI application & Safe AST engine
    ├── test_calculator.py   # Automated unit tests (17 test cases)
    └── README.md            # Comprehensive documentation & setup guide
```

---

## 🎯 Technical Decisions & Interview Talking Points

1. **Why is `eval()` strictly forbidden in professional software?**
   In Python, `eval("__import__('os').system('rmdir /s /q ...')")` executes arbitrary code with the full permissions of the running user. Using `eval()` directly on user input is classified under OWASP as a **Remote Code Execution (RCE) / Code Injection** vulnerability.
   
2. **How does the AST Safe Evaluator work?**
   Using `ast.parse(expr, mode='eval')`, Python compiles the string into a syntax tree without executing it. We then traverse the tree and **only allow** whitelist nodes (`ast.BinOp`, `ast.Constant`, `ast.Add`, `ast.Sub`, `ast.Mult`, `ast.Div`, `ast.Mod`). If any function calls, variable names, or loops appear, a `ValueError` is raised immediately.

3. **How does the GUI prevent floating-point representation bugs?**
   Computers store floats in IEEE 754 binary, which can cause expressions like `0.1 + 0.2` to yield `0.30000000000000004`. The engine uses `round(result, 10)` and formatting with `:g` or integer checks to display clean, human-readable numbers like `0.3`.
