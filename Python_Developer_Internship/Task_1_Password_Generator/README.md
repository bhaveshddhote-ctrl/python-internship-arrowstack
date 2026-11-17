# Task 1: Secure Password Generator

A customizable, cryptographically secure Command-Line Interface (CLI) password generator built with Python 3 using only the standard library.

Developed as part of the **Python Developer Internship**.

---

## 📌 Project Overview

This application allows users to generate one or multiple high-entropy, cryptographically strong passwords tailored to specific security requirements. Unlike standard random generators, it leverages Python's `secrets` module, making the output resilient against brute-force and dictionary attacks.

---

## ✨ Features

- **Cryptographically Secure**: Built with Python's `secrets` module (OS-level CSPRNG) instead of the predictable `random` module.
- **Customizable Character Categories**:
  - Uppercase letters (`A-Z`)
  - Lowercase letters (`a-z`)
  - Digits (`0-9`)
  - Special symbols (`!@#$%^&*()-_=+[]{}|;:,.<>?/~`)
- **Guaranteed Category Inclusion**: Guarantees at least one character from each enabled category, then shuffles positions to avoid predictable patterns.
- **Input Validation & Crash Resilience**: Gracefully handles non-integers, negative numbers, lengths smaller than selected categories, and empty category selections.
- **Batch Generation**: Generate between 1 and 50 passwords in a single run.
- **Interactive Session Loop**: Generate multiple batches or exit cleanly without restarting the script.
- **Zero Dependencies**: Uses strictly the Python 3 standard library.
- **Zero Logging / Privacy**: Passwords are displayed only on the user's terminal and are never saved to disk or logged.

---

## 🛠️ Prerequisites

- **Python**: Version 3.8 or higher (Tested on Python 3.14)
- **Dependencies**: None (Uses built-in standard library: `secrets`, `string`, `sys`, `unittest`)

---

## 🚀 How to Run the Application

Open your terminal or PowerShell in the project directory and run:

```bash
python Python_Developer_Internship/Task_1_Password_Generator/password_generator.py
```

### Example Interactive Session:

```text
*******************************************************
*                                                     *
*      PYTHON INTERNSHIP: TASK 1 - PASSWORD GENERATOR   *
*         (Cryptographically Secure & Customizable)     *
*                                                     *
*******************************************************

--- Character Category Selection ---
Choose which character types to include in your password:
Include Uppercase letters (A-Z)? [Y/n]: y
Include Lowercase letters (a-z)? [Y/n]: y
Include Digits (0-9)? [Y/n]: y
Include Special Symbols (!@#$..)? [Y/n]: y

Enter desired password length (minimum 4, recommended 12-16): 14
How many passwords would you like to generate? (1-50): 3

==================================================
  Generated Password(s) [3 total]:
==================================================
  [01]  ;@@EeV3N&h,V0p
  [02]  ]+:lX,&iG{uNP5
  [03]  9#Kx~mQ7!bLw$2
==================================================
  [Tip] Store your passwords in a secure password manager.
==================================================

Would you like to generate more passwords? [Y/n]: n

Thank you for using the Password Generator. Stay secure!
```

---

## 🧪 How to Run Automated Tests

The project includes a comprehensive automated test suite in `test_password_generator.py` covering:
1. Output length verification.
2. Guaranteed presence of every enabled category.
3. Strict exclusion of disabled categories.
4. Single-category edge cases (e.g., numeric PIN generation).
5. Minimum boundary lengths.
6. Error handling for invalid lengths and empty category selections.
7. Batch generation count and uniqueness.

Run the tests with:

```bash
python Python_Developer_Internship/Task_1_Password_Generator/test_password_generator.py -v
```

### Expected Output:

```text
test_boundary_case_minimum_length ... ok
test_default_generation_length ... ok
test_disabled_categories_are_strictly_excluded ... ok
test_generate_multiple_passwords ... ok
test_guaranteed_category_inclusion_all ... ok
test_length_less_than_categories_raises_value_error ... ok
test_no_categories_selected_raises_value_error ... ok
test_single_category_only ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.009s

OK
```

---

## 📁 Project Structure

```text
Python_Developer_Internship/
└── Task_1_Password_Generator/
    ├── password_generator.py       # Main CLI application
    ├── test_password_generator.py  # Automated unit test suite
    └── README.md                   # Project documentation & instructions
```

---

## 🎯 Technical Decisions & Interview Talking Points

1. **Why `secrets` instead of `random`?**
   Python's `random` module uses the Mersenne Twister PRNG, which produces deterministic sequences if an attacker observes ~624 generated values. The `secrets` module uses OS entropy (`/dev/urandom` or `CryptGenRandom`), which is cryptographically secure.

2. **How is category requirement guaranteed?**
   Rather than randomly generating until a condition is met (which is inefficient), the algorithm explicitly picks one character from each enabled set, fills the remaining length from the combined pool, and then securely shuffles the resulting list.

3. **Input Validation Strategy**:
   Uses standard `while True` loops with `try-except ValueError` blocks to continuously prompt the user until valid data is provided, preventing crashes and offering clear error messages.
