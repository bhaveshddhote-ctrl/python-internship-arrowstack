from datetime import datetime
import json
import os
import sys

# Enable ANSI escape code support on Windows terminals
if os.name == "nt":
    os.system("")

# Persistent JSON storage path anchored to the script location
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

# ANSI Color Codes for Modern Terminal UI
class UI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


# Allowed Priorities & Categories
PRIORITIES = ["High", "Medium", "Low"]
DEFAULT_CATEGORIES = ["Work", "Personal", "Study", "General"]


# ---------------------------------------------------------------------------
# Storage & Persistence Layer
# ---------------------------------------------------------------------------

def load_tasks(file_path: str = DATA_FILE) -> list:
    """Load tasks from JSON storage with backward compatibility for legacy tasks.

    Handles missing files, empty files, and malformed JSON safely.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return []
            raw_data = json.loads(content)

            if not isinstance(raw_data, list):
                print(f"{UI.YELLOW}  [Warning] Task file format was invalid. Starting empty.{UI.RESET}")
                return []

            # Normalize data to ensure all fields exist (backward compatibility)
            normalized_tasks = []
            for item in raw_data:
                if isinstance(item, dict) and "id" in item and "title" in item:
                    item.setdefault("priority", "Medium")
                    item.setdefault("category", "General")
                    item.setdefault("completed", False)
                    item.setdefault("created_at", "N/A")
                    item.setdefault("completed_at", None)
                    normalized_tasks.append(item)
            return normalized_tasks

    except (json.JSONDecodeError, OSError) as err:
        print(f"{UI.YELLOW}  [Warning] Could not parse '{os.path.basename(file_path)}': {err}")
        print(f"            Starting with a safe session to prevent data loss.{UI.RESET}")
        return []


def save_tasks(tasks: list, file_path: str = DATA_FILE) -> bool:
    """Save tasks to JSON with 4-space indentation for human readability."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)
        return True
    except OSError as err:
        print(f"{UI.RED}  [Error] Failed to save tasks to '{os.path.basename(file_path)}': {err}{UI.RESET}")
        return False


def get_next_task_id(tasks: list) -> int:
    """Generate a unique, stable ID for a new task."""
    if not tasks:
        return 1
    existing_ids = [t.get("id", 0) for t in tasks if isinstance(t.get("id"), int)]
    return max(existing_ids, default=0) + 1


# ---------------------------------------------------------------------------
# Business Logic (CRUD Operations)
# ---------------------------------------------------------------------------

def add_task(
    tasks: list,
    title: str,
    priority: str = "Medium",
    category: str = "General",
) -> dict:
    """Create a new task with priority, category, and creation timestamp."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Task title cannot be empty.")

    clean_priority = priority.capitalize() if priority.capitalize() in PRIORITIES else "Medium"
    clean_category = category.strip().capitalize() if category.strip() else "General"

    new_task = {
        "id": get_next_task_id(tasks),
        "title": clean_title,
        "priority": clean_priority,
        "category": clean_category,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed_at": None,
    }
    tasks.append(new_task)
    return new_task


def mark_task_completed(tasks: list, task_id: int) -> bool:
    """Mark a task as completed and record completion timestamp."""
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            return True
    return False


def toggle_task_status(tasks: list, task_id: int) -> dict:
    """Toggle task status between completed and pending."""
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = not task.get("completed", False)
            if task["completed"]:
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            else:
                task["completed_at"] = None
            return task
    return None


def edit_task(
    tasks: list,
    task_id: int,
    new_title: str = None,
    new_priority: str = None,
    new_category: str = None,
) -> dict:
    """Update title, priority, or category of an existing task."""
    for task in tasks:
        if task.get("id") == task_id:
            if new_title is not None and new_title.strip():
                task["title"] = new_title.strip()
            if new_priority is not None and new_priority.capitalize() in PRIORITIES:
                task["priority"] = new_priority.capitalize()
            if new_category is not None and new_category.strip():
                task["category"] = new_category.strip().capitalize()
            return task
    return None


def delete_task(tasks: list, task_id: int) -> dict:
    """Delete a task by ID."""
    for idx, task in enumerate(tasks):
        if task.get("id") == task_id:
            return tasks.pop(idx)
    return None


def clear_completed_tasks(tasks: list) -> int:
    """Remove all completed tasks from the list. Returns number of tasks removed."""
    initial_count = len(tasks)
    tasks[:] = [t for t in tasks if not t.get("completed", False)]
    return initial_count - len(tasks)


# ---------------------------------------------------------------------------
# UI Helpers & Formatting
# ---------------------------------------------------------------------------

def render_progress_bar(completed: int, total: int, width: int = 24) -> str:
    """Return a styled ASCII/Unicode progress bar."""
    if total == 0:
        return f"{UI.GRAY}[{'-' * width}] 0% (0/0 tasks){UI.RESET}"

    percentage = (completed / total) * 100
    filled = int(round(width * completed / float(total)))
    bar = "=" * filled + "-" * (width - filled)
    color = UI.GREEN if percentage == 100 else (UI.CYAN if percentage >= 50 else UI.YELLOW)

    return f"{color}[{bar}] {percentage:5.1f}% ({completed}/{total} completed){UI.RESET}"


def format_priority_badge(priority: str) -> str:
    """Return color-coded priority badge."""
    p = str(priority).capitalize()
    if p == "High":
        return f"{UI.RED}[High  ]{UI.RESET}"
    if p == "Medium":
        return f"{UI.YELLOW}[Medium]{UI.RESET}"
    return f"{UI.GRAY}[Low   ]{UI.RESET}"


def format_status_badge(completed: bool) -> str:
    """Return color-coded status indicator."""
    if completed:
        return f"{UI.GREEN}[Done   ]{UI.RESET}"
    return f"{UI.YELLOW}[Pending]{UI.RESET}"


def display_dashboard(tasks: list, filter_label: str = "All Tasks") -> None:
    """Display modern table dashboard with statistics and progress bar."""
    total = len(tasks)
    completed_count = sum(1 for t in tasks if t.get("completed", False))
    pending_count = total - completed_count
    high_count = sum(1 for t in tasks if t.get("priority") == "High" and not t.get("completed", False))

    print("\n" + f"{UI.CYAN}" + "=" * 80 + f"{UI.RESET}")
    print(f"{UI.BOLD}{UI.WHITE}  * TO-DO DASHBOARD PRO  |  Filter: {filter_label}{UI.RESET}")
    print(f"{UI.CYAN}" + "=" * 80 + f"{UI.RESET}")

    # Progress bar and quick summary stats
    print(f"  Progress : {render_progress_bar(completed_count, total)}")
    print(
        f"  Metrics  : {UI.BOLD}{total}{UI.RESET} Total  |  "
        f"{UI.GREEN}{completed_count} Done{UI.RESET}  |  "
        f"{UI.YELLOW}{pending_count} Pending{UI.RESET}  |  "
        f"{UI.RED}{high_count} Urgent (High Priority){UI.RESET}"
    )
    print(f"{UI.CYAN}" + "-" * 80 + f"{UI.RESET}")

    if not tasks:
        print(f"\n  {UI.GRAY}(No tasks found matching this criteria){UI.RESET}\n")
        print(f"{UI.CYAN}" + "=" * 80 + f"{UI.RESET}\n")
        return

    # Table Header
    print(
        f" {UI.BOLD}{'ID':<5} {'Status':<11} {'Priority':<10} {'Category':<12} {'Created':<17} {'Task Title'}{UI.RESET}"
    )
    print(f"{UI.GRAY}" + "-" * 80 + f"{UI.RESET}")

    for task in tasks:
        t_id = str(task.get("id", "-"))
        status = format_status_badge(task.get("completed", False))
        priority = format_priority_badge(task.get("priority", "Medium"))
        category = f"{UI.MAGENTA}{task.get('category', 'General')[:11]:<12}{UI.RESET}"
        created = f"{UI.GRAY}{task.get('created_at', 'N/A')[:16]:<17}{UI.RESET}"
        title = task.get("title", "(No title)")

        # Strike-through effect or dim for completed tasks
        if task.get("completed", False):
            title = f"{UI.DIM}{UI.GRAY}{title}{UI.RESET}"
        else:
            title = f"{UI.WHITE}{title}{UI.RESET}"

        print(f" {t_id:<5} {status} {priority} {category} {created} {title}")

    print(f"{UI.CYAN}" + "=" * 80 + f"{UI.RESET}\n")


def print_main_menu() -> None:
    """Render the main navigation menu."""
    print(f"{UI.BLUE}+{'=' * 62}+{UI.RESET}")
    print(f"{UI.BLUE}|{UI.BOLD}{UI.CYAN}            * TO-DO LIST APPLICATION PRO (CLI) *              {UI.BLUE}|{UI.RESET}")
    print(f"{UI.BLUE}+{'=' * 62}+{UI.RESET}")
    print(f"{UI.BLUE}|{UI.WHITE}  [1] View Dashboard & Tasks     [2] Add New Task            {UI.BLUE}|{UI.RESET}")
    print(f"{UI.BLUE}|{UI.WHITE}  [3] Toggle Status (Done/Todo)  [4] Edit Task Details       {UI.BLUE}|{UI.RESET}")
    print(f"{UI.BLUE}|{UI.WHITE}  [5] Delete Task                [6] Search & Filter Tasks   {UI.BLUE}|{UI.RESET}")
    print(f"{UI.BLUE}|{UI.WHITE}  [7] Clear Completed Tasks      [8] Save & Exit             {UI.BLUE}|{UI.RESET}")
    print(f"{UI.BLUE}+{'=' * 62}+{UI.RESET}")


# ---------------------------------------------------------------------------
# Interactive Command Handlers
# ---------------------------------------------------------------------------

def prompt_choice(prompt: str, options: list, default: str) -> str:
    """Prompt user to choose from a list of options with a default value."""
    formatted_options = "/".join(
        f"[{opt}]" if opt.lower() == default.lower() else opt for opt in options
    )
    user_input = input(f"{prompt} ({formatted_options}): ").strip()
    if not user_input:
        return default
    for opt in options:
        if user_input.lower() == opt.lower():
            return opt
    print(f"  {UI.YELLOW}[!] Unrecognized choice. Defaulting to '{default}'.{UI.RESET}")
    return default


def handle_add_task(tasks: list) -> None:
    """Interactive handler for adding a task with priority and category."""
    print(f"\n{UI.BOLD}--- Add New Task ---{UI.RESET}")
    while True:
        title = input("Enter task title (or 'cancel'): ").strip()
        if not title:
            print(f"  {UI.RED}[!] Task title cannot be empty.{UI.RESET}")
            continue
        if title.lower() == "cancel":
            print(f"  {UI.GRAY}[Action Cancelled]{UI.RESET}")
            return

        priority = prompt_choice("Select priority", PRIORITIES, default="Medium")
        category_input = input("Enter category (e.g., Work, Study, Personal) [General]: ").strip()
        category = category_input if category_input else "General"

        new_task = add_task(tasks, title=title, priority=priority, category=category)
        save_tasks(tasks)
        print(f"\n  {UI.GREEN}[Success] Task #{new_task['id']} added successfully! [{priority} | {category}]{UI.RESET}\n")
        break


def handle_toggle_status(tasks: list) -> None:
    """Toggle a task between Completed and Pending."""
    if not tasks:
        print(f"\n  {UI.YELLOW}[!] No tasks available to update.{UI.RESET}\n")
        return

    display_dashboard(tasks, filter_label="Quick View for Status Toggle")
    while True:
        raw_id = input("Enter Task ID to toggle status (or 'cancel'): ").strip()
        if raw_id.lower() == "cancel":
            return
        try:
            task_id = int(raw_id)
            updated = toggle_task_status(tasks, task_id)
            if updated:
                save_tasks(tasks)
                new_state = "Completed" if updated["completed"] else "Marked as Pending"
                print(f"\n  {UI.GREEN}[Success] Task #{task_id} is now {new_state}!{UI.RESET}\n")
                break
            print(f"  {UI.RED}[!] Task ID #{task_id} not found.{UI.RESET}")
        except ValueError:
            print(f"  {UI.RED}[!] Please enter a valid numeric ID.{UI.RESET}")


def handle_edit_task(tasks: list) -> None:
    """Interactive handler for updating title, priority, or category."""
    if not tasks:
        print(f"\n  {UI.YELLOW}[!] No tasks available to edit.{UI.RESET}\n")
        return

    display_dashboard(tasks, filter_label="Select Task to Edit")
    while True:
        raw_id = input("Enter Task ID to edit (or 'cancel'): ").strip()
        if raw_id.lower() == "cancel":
            return
        try:
            task_id = int(raw_id)
            target = next((t for t in tasks if t.get("id") == task_id), None)
            if not target:
                print(f"  {UI.RED}[!] Task ID #{task_id} not found.{UI.RESET}")
                continue

            print(f"\nEditing Task #{task_id} (Leave blank to keep current value):")
            print(f" Current Title    : {target['title']}")
            new_title = input(" New Title        : ").strip()

            print(f" Current Priority : {target.get('priority', 'Medium')}")
            new_priority = input(f" New Priority ({'/'.join(PRIORITIES)}) : ").strip()

            print(f" Current Category : {target.get('category', 'General')}")
            new_category = input(" New Category     : ").strip()

            edit_task(
                tasks,
                task_id,
                new_title=new_title if new_title else None,
                new_priority=new_priority if new_priority else None,
                new_category=new_category if new_category else None,
            )
            save_tasks(tasks)
            print(f"\n  {UI.GREEN}[Success] Task #{task_id} updated successfully!{UI.RESET}\n")
            break
        except ValueError:
            print(f"  {UI.RED}[!] Please enter a valid numeric ID.{UI.RESET}")


def handle_delete_task(tasks: list) -> None:
    """Interactive handler for deleting a task with confirmation."""
    if not tasks:
        print(f"\n  {UI.YELLOW}[!] No tasks available to delete.{UI.RESET}\n")
        return

    display_dashboard(tasks, filter_label="Select Task to Delete")
    while True:
        raw_id = input("Enter Task ID to delete (or 'cancel'): ").strip()
        if raw_id.lower() == "cancel":
            return
        try:
            task_id = int(raw_id)
            deleted = delete_task(tasks, task_id)
            if deleted:
                save_tasks(tasks)
                print(f"\n  {UI.GREEN}[Success] Task #{task_id} ('{deleted['title']}') was deleted.{UI.RESET}\n")
                break
            print(f"  {UI.RED}[!] Task ID #{task_id} not found.{UI.RESET}")
        except ValueError:
            print(f"  {UI.RED}[!] Please enter a valid numeric ID.{UI.RESET}")


def handle_search_and_filter(tasks: list) -> None:
    """Filter tasks by status, priority, or search term."""
    if not tasks:
        print(f"\n  {UI.YELLOW}[!] Task list is empty.{UI.RESET}\n")
        return

    print(f"\n{UI.BOLD}--- Search & Filter Options ---{UI.RESET}")
    print(" 1. Filter by Pending Only")
    print(" 2. Filter by Completed Only")
    print(" 3. Filter by High Priority")
    print(" 4. Search by Keyword in Title")
    print(" 5. Return to Main Menu")

    choice = input("Select an option (1-5): ").strip()
    if choice == "1":
        filtered = [t for t in tasks if not t.get("completed", False)]
        display_dashboard(filtered, filter_label="Pending Tasks Only")
    elif choice == "2":
        filtered = [t for t in tasks if t.get("completed", False)]
        display_dashboard(filtered, filter_label="Completed Tasks Only")
    elif choice == "3":
        filtered = [t for t in tasks if t.get("priority") == "High"]
        display_dashboard(filtered, filter_label="High Priority Tasks")
    elif choice == "4":
        query = input("Enter search keyword: ").strip().lower()
        filtered = [t for t in tasks if query in t.get("title", "").lower()]
        display_dashboard(filtered, filter_label=f"Search Results for '{query}'")
    else:
        print("  [Returning to Main Menu]")


def handle_clear_completed(tasks: list) -> None:
    """Clear all completed tasks after confirmation."""
    completed_count = sum(1 for t in tasks if t.get("completed", False))
    if completed_count == 0:
        print(f"\n  {UI.YELLOW}[Info] There are no completed tasks to clear.{UI.RESET}\n")
        return

    confirm = input(f"Are you sure you want to remove all {completed_count} completed tasks? (y/N): ").strip().lower()
    if confirm in {"y", "yes"}:
        removed = clear_completed_tasks(tasks)
        save_tasks(tasks)
        print(f"\n  {UI.GREEN}[Success] Successfully cleared {removed} completed tasks!{UI.RESET}\n")
    else:
        print(f"  {UI.GRAY}[Action Cancelled]{UI.RESET}\n")


# ---------------------------------------------------------------------------
# Main Application Loop
# ---------------------------------------------------------------------------

def main() -> None:
    """Main application loop with defensive exception handling."""
    tasks = load_tasks()

    while True:
        try:
            print_main_menu()
            choice = input(f"{UI.BOLD}Enter your choice (1-8): {UI.RESET}").strip()

            if choice == "1":
                display_dashboard(tasks, filter_label="All Tasks")
            elif choice == "2":
                handle_add_task(tasks)
            elif choice == "3":
                handle_toggle_status(tasks)
            elif choice == "4":
                handle_edit_task(tasks)
            elif choice == "5":
                handle_delete_task(tasks)
            elif choice == "6":
                handle_search_and_filter(tasks)
            elif choice == "7":
                handle_clear_completed(tasks)
            elif choice == "8":
                save_tasks(tasks)
                print(f"\n{UI.GREEN}[Success] All tasks safely stored in 'tasks.json'. Thank you for using To-Do Pro!{UI.RESET}\n")
                sys.exit(0)
            else:
                print(f"\n  {UI.RED}[!] Invalid selection. Please enter a number between 1 and 8.{UI.RESET}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{UI.CYAN}Saving tasks before exit...{UI.RESET}")
            save_tasks(tasks)
            print(f"{UI.GREEN}Goodbye! Stay productive!{UI.RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
