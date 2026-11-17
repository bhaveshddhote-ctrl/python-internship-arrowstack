# Task 2: Professional To-Do List Application PRO (CLI)

An advanced, feature-rich Command-Line Interface (CLI) task management suite built with Python 3 using persistent JSON storage, ANSI color-coded dashboards, and robust validation.

Developed as part of the **Auspify Technologies Python Developer Internship**.

---

## 📌 Project Overview

While basic to-do lists only allow simple string lists, this **Professional To-Do Manager Pro** is built for real-world productivity. It implements full **CRUD operations**, **Priority Levels**, **Categorization**, **Search & Filter**, **Real-Time Progress Tracking**, and **Task Editing**, all while strictly using Python's standard library with zero third-party dependencies.

---

## ✨ Advanced Features

1. **Dashboard & Visual Metrics**:
   - Dynamic ASCII/ANSI **Real-time Progress Bar**: e.g. `[================--------] 66.7% (2/3 completed)`
   - Live metrics summary: Total tasks, Done, Pending, and Urgent (High Priority) counts.
2. **Prioritization & Badges**:
   - Assign priority levels: `High` (Red badge), `Medium` (Yellow badge), `Low` (Gray badge).
3. **Categorization**:
   - Organize tasks by tags (e.g., `Work`, `Personal`, `Study`, `General`).
4. **Timestamps**:
   - Automatic `created_at` timestamping (`YYYY-MM-DD HH:MM`).
   - Automatic `completed_at` recording upon task completion.
5. **Interactive Status Toggling**:
   - Option [3] allows toggling any task between `Completed` and `Pending`.
6. **Task Editing (Update)**:
   - Edit task title, priority, or category in-place without deleting and recreating.
7. **Search & Smart Filtering**:
   - Filter by **Pending Only**.
   - Filter by **Completed Only**.
   - Filter by **High Priority (Urgent)**.
   - Search by **keyword** in task titles.
8. **Batch Operations**:
   - Clear all completed tasks at once with confirmation prompt.
9. **Persistent JSON Storage & Backward Compatibility**:
   - Safely reads and writes to `tasks.json`.
   - Automatically migrates and populates default fields for legacy task records without data loss.
10. **Crash-Proof Cross-Platform UI**:
    - Uses ANSI color codes compatible with modern Windows Terminal, PowerShell, CMD, Linux, and macOS.
    - Uses 100% portable ASCII borders avoiding `cp1252` encoding errors.

---

## 🛠️ Prerequisites

- **Python**: Version 3.8 or higher (Tested on Python 3.14)
- **External Packages**: None (Uses built-in standard library: `json`, `os`, `sys`, `datetime`, `unittest`)

---

## 🚀 How to Run the Application

Open your terminal or PowerShell in the root directory and execute:

```bash
python Python_Developer_Internship/Task_2_Todo_List/main.py
```

### Dashboard & Menu Preview:

```text
+==============================================================+
|            * TO-DO LIST APPLICATION PRO (CLI) *              |
+==============================================================+
|  [1] View Dashboard & Tasks     [2] Add New Task            |
|  [3] Toggle Status (Done/Todo)  [4] Edit Task Details       |
|  [5] Delete Task                [6] Search & Filter Tasks   |
|  [7] Clear Completed Tasks      [8] Save & Exit             |
+==============================================================+
Enter your choice (1-8): 1

================================================================================
  * TO-DO DASHBOARD PRO  |  Filter: All Tasks
================================================================================
  Progress : [================--------]  66.7% (2/3 completed)
  Metrics  : 3 Total  |  2 Done  |  1 Pending  |  0 Urgent (High Priority)
--------------------------------------------------------------------------------
 ID    Status      Priority   Category     Created           Task Title
--------------------------------------------------------------------------------
 2     [Done   ]   [Medium]   Work         2026-10-23 23:30  Prepare presentation
 3     [Pending]   [High  ]   Internship   2026-10-23 23:35  Complete Task 2
 4     [Done   ]   [Low   ]   General      2026-10-23 23:38  bhavesh project
================================================================================
```

---

## 🧪 How to Run Automated Tests

The test suite in `test_todo_app.py` verifies all features:
1. Adding tasks with metadata (Priority, Category, Timestamps).
2. Blank title rejection.
3. Status toggling and completion timestamps.
4. In-place task editing.
5. Deleting tasks and stable ID generation.
6. Clearing completed tasks.
7. JSON file persistence and backward compatibility.
8. Resilience against corrupted or missing JSON files.

Run the test suite with:

```bash
python Python_Developer_Internship/Task_2_Todo_List/test_todo_app.py -v
```

### Verified Test Run:

```text
test_add_task_with_metadata ... ok
test_clear_completed_tasks ... ok
test_corrupt_file_resilience ... ok
test_delete_task ... ok
test_edit_task_details ... ok
test_empty_task_title_validation ... ok
test_json_persistence_and_backward_compatibility ... ok
test_toggle_task_status ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.022s

OK
```

---

## 📁 Project Structure

```text
Python_Developer_Internship/
└── Task_2_Todo_List/
    ├── main.py             # Advanced CLI application with Dashboard & Features
    ├── tasks.json          # Persistent JSON database (auto-created & synced)
    ├── test_todo_app.py    # Automated test suite (unittest)
    └── README.md           # Documentation, guide, and interview notes
```

---

## 🎯 Technical Decisions & Interview Talking Points

1. **Why add Priority and Categories to a CLI app?**
   In enterprise environments, tasks are rarely flat text lists. Organizing tasks by Priority (`High`, `Medium`, `Low`) and Category (`Work`, `Personal`, etc.) enables meaningful filtering and triage.

2. **How does the Progress Bar work without external libraries?**
   Using standard Python string multiplication and formatted floats:
   ```python
   filled = int(round(width * completed / total))
   bar = "=" * filled + "-" * (width - filled)
   ```
   This gives an immediate, visually appealing overview of progress without needing heavy external packages like `rich` or `tqdm`.

3. **Backward Compatibility Strategy**:
   When new fields like `priority` and `created_at` were introduced, `load_tasks()` was designed defensively using `item.setdefault(...)` so that previously created JSON records from older versions load smoothly without breaking.
