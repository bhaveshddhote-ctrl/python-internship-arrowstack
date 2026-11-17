"""
Task 1: Password Generator
Internship Project: Python Developer Internship
Description: A beginner-friendly, secure, and customizable CLI password generator.
Built using Python's standard library (secrets, string) following PEP 8.
"""

import secrets
import string
import sys

# Define character sets using standard library constants
UPPERCASE_CHARS = string.ascii_uppercase
LOWERCASE_CHARS = string.ascii_lowercase
DIGIT_CHARS = string.digits
# Special symbols suitable for passwords
SYMBOL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"


def get_yes_no_choice(prompt: str, default: str = "y") -> bool:
    """Prompt the user for a Yes/No decision with input validation.

    Accepts 'y', 'yes', 'n', 'no' (case-insensitive).
    """
    valid_yes = {"y", "yes"}
    valid_no = {"n", "no"}
    suffix = " [Y/n]: " if default == "y" else " [y/N]: "

    while True:
        try:
            user_input = input(prompt + suffix).strip().lower()
            if not user_input:
                return default == "y"
            if user_input in valid_yes:
                return True
            if user_input in valid_no:
                return False
            print("  [!] Please enter 'y' for Yes or 'n' for No.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user. Exiting...")
            sys.exit(0)


def get_integer_input(prompt: str, min_value: int = 1, max_value: int = 512) -> int:
    """Prompt the user for an integer within a specified range [min_value, max_value].

    Handles invalid inputs (strings, floats, negatives) gracefully without crashing.
    """
    while True:
        try:
            raw_val = input(prompt).strip()
            val = int(raw_val)
            if val < min_value:
                print(f"  [!] Value must be at least {min_value}. Please try again.")
                continue
            if val > max_value:
                print(f"  [!] Value cannot exceed {max_value}. Please try again.")
                continue
            return val
        except ValueError:
            print("  [!] Invalid input. Please enter a valid whole number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user. Exiting...")
            sys.exit(0)


def get_character_preferences() -> dict:
    """Ask user which character sets to include.

    Ensures that at least one character category is selected.
    """
    print("\n--- Character Category Selection ---")
    print("Choose which character types to include in your password:")

    while True:
        use_upper = get_yes_no_choice("Include Uppercase letters (A-Z)?", default="y")
        use_lower = get_yes_no_choice("Include Lowercase letters (a-z)?", default="y")
        use_digits = get_yes_no_choice("Include Digits (0-9)?", default="y")
        use_symbols = get_yes_no_choice("Include Special Symbols (!@#$..)?", default="y")

        if use_upper or use_lower or use_digits or use_symbols:
            return {
                "upper": use_upper,
                "lower": use_lower,
                "digits": use_digits,
                "symbols": use_symbols,
            }

        print("\n  [!] Error: You must select at least ONE character category.")
        print("      Please make your selections again.\n")


def generate_single_password(
    length: int,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a cryptographically secure random password.

    Requirements:
    - Uses Python's `secrets` module (CSPRNG).
    - Guarantees at least one character from each enabled category.
    - Shuffles the final list to avoid predictable character positions.
    """
    categories_selected = []
    combined_pool = ""

    if use_upper:
        categories_selected.append(UPPERCASE_CHARS)
        combined_pool += UPPERCASE_CHARS
    if use_lower:
        categories_selected.append(LOWERCASE_CHARS)
        combined_pool += LOWERCASE_CHARS
    if use_digits:
        categories_selected.append(DIGIT_CHARS)
        combined_pool += DIGIT_CHARS
    if use_symbols:
        categories_selected.append(SYMBOL_CHARS)
        combined_pool += SYMBOL_CHARS

    if not categories_selected:
        raise ValueError("At least one character category must be enabled.")

    min_required_length = len(categories_selected)
    if length < min_required_length:
        raise ValueError(
            f"Length ({length}) must be at least {min_required_length} to include "
            f"all {min_required_length} selected character categories."
        )

    # Step 1: Guarantee at least one character from each enabled category
    password_chars = [secrets.choice(category) for category in categories_selected]

    # Step 2: Fill remaining slots by randomly choosing from the full combined pool
    remaining_slots = length - len(password_chars)
    for _ in range(remaining_slots):
        password_chars.append(secrets.choice(combined_pool))

    # Step 3: Cryptographically shuffle the characters so guaranteed items
    # are not always at the front of the password
    secure_rng = secrets.SystemRandom()
    secure_rng.shuffle(password_chars)

    return "".join(password_chars)


def generate_multiple_passwords(count: int, length: int, prefs: dict) -> list:
    """Generate 'count' distinct secure passwords with the specified preferences."""
    passwords = []
    for _ in range(count):
        pwd = generate_single_password(
            length=length,
            use_upper=prefs["upper"],
            use_lower=prefs["lower"],
            use_digits=prefs["digits"],
            use_symbols=prefs["symbols"],
        )
        passwords.append(pwd)
    return passwords


def display_passwords(passwords: list) -> None:
    """Display the generated passwords clearly in the terminal with index numbers."""
    print("\n" + "=" * 50)
    print(f"  Generated Password(s) [{len(passwords)} total]:")
    print("=" * 50)
    for idx, pwd in enumerate(passwords, start=1):
        print(f"  [{idx:02d}]  {pwd}")
    print("=" * 50)
    print("  [Tip] Store your passwords in a secure password manager.")
    print("=" * 50 + "\n")


def print_banner() -> None:
    """Print a clean welcome header."""
    print("*" * 55)
    print("*" + " " * 53 + "*")
    print("*      PYTHON INTERNSHIP: TASK 1 - PASSWORD GENERATOR   *")
    print("*         (Cryptographically Secure & Customizable)     *")
    print("*" + " " * 53 + "*")
    print("*" * 55)


def run_session() -> None:
    """Run a single password generation session."""
    # 1. Get character categories
    prefs = get_character_preferences()
    selected_count = sum(1 for val in prefs.values() if val)

    # 2. Get password length (must be >= selected_count)
    prompt = (
        f"\nEnter desired password length (minimum {selected_count}, recommended 12-16): "
    )
    length = get_integer_input(prompt, min_value=selected_count, max_value=256)

    # 3. Get quantity of passwords to generate
    count_prompt = "How many passwords would you like to generate? (1-50): "
    count = get_integer_input(count_prompt, min_value=1, max_value=50)

    # 4. Generate passwords
    passwords = generate_multiple_passwords(count, length, prefs)

    # 5. Display output clearly
    display_passwords(passwords)


def main() -> None:
    """Main application loop."""
    print_banner()

    while True:
        try:
            run_session()
            again = get_yes_no_choice("Would you like to generate more passwords?", default="y")
            if not again:
                print("\nThank you for using the Password Generator. Stay secure!\n")
                break
        except (KeyboardInterrupt, EOFError):
            print("\n\nProgram terminated by user. Goodbye!")
            break


if __name__ == "__main__":
    main()
