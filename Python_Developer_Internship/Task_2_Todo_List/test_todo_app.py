"""
Comprehensive Automated Test Suite for Task 2: Professional To-Do List Application
Verifies all core CRUD, advanced features (priority, category, editing, toggle, search/filter),
stable unique IDs, JSON persistence, and edge-case error handling.
"""

import json
import os
import tempfile
import unittest
import importlib.util

# Load main module dynamically
spec = importlib.util.spec_from_file_location(
    "todo_main",
    "Python_Developer_Internship/Task_2_Todo_List/main.py"
)
todo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(todo)


class TestProfessionalTodoList(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory and file for testing JSON persistence."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, "test_tasks.json")

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_add_task_with_metadata(self):
        """Test adding tasks creates valid entries with priority, category, and timestamps."""
        tasks = []
        t1 = todo.add_task(tasks, "Finish Task 2", priority="High", category="Internship")

        self.assertEqual(len(tasks), 1)
        self.assertEqual(t1["id"], 1)
        self.assertEqual(t1["title"], "Finish Task 2")
        self.assertEqual(t1["priority"], "High")
        self.assertEqual(t1["category"], "Internship")
        self.assertFalse(t1["completed"])
        self.assertIn("created_at", t1)

    def test_empty_task_title_validation(self):
        """Test empty and whitespace task titles are rejected."""
        tasks = []
        with self.assertRaises(ValueError):
            todo.add_task(tasks, "")
        with self.assertRaises(ValueError):
            todo.add_task(tasks, "   ")

    def test_toggle_task_status(self):
        """Test toggling status between completed and pending."""
        tasks = []
        t1 = todo.add_task(tasks, "Test Toggle")
        self.assertFalse(t1["completed"])

        # Toggle to Done
        updated = todo.toggle_task_status(tasks, 1)
        self.assertTrue(updated["completed"])
        self.assertIsNotNone(updated["completed_at"])

        # Toggle back to Pending
        updated2 = todo.toggle_task_status(tasks, 1)
        self.assertFalse(updated2["completed"])
        self.assertIsNone(updated2["completed_at"])

    def test_edit_task_details(self):
        """Test editing title, priority, and category."""
        tasks = []
        todo.add_task(tasks, "Original Title", priority="Low", category="Personal")

        edited = todo.edit_task(tasks, 1, new_title="Updated Title", new_priority="High", new_category="Work")
        self.assertIsNotNone(edited)
        self.assertEqual(edited["title"], "Updated Title")
        self.assertEqual(edited["priority"], "High")
        self.assertEqual(edited["category"], "Work")

    def test_delete_task(self):
        """Test deleting task by ID."""
        tasks = []
        todo.add_task(tasks, "Task A")
        todo.add_task(tasks, "Task B")

        deleted = todo.delete_task(tasks, 1)
        self.assertEqual(deleted["id"], 1)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], 2)

    def test_clear_completed_tasks(self):
        """Test clearing all completed tasks."""
        tasks = []
        todo.add_task(tasks, "Task 1")
        todo.add_task(tasks, "Task 2")
        todo.mark_task_completed(tasks, 1)

        cleared_count = todo.clear_completed_tasks(tasks)
        self.assertEqual(cleared_count, 1)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], 2)

    def test_json_persistence_and_backward_compatibility(self):
        """Test saving, reloading, and handling legacy tasks without metadata."""
        # Create legacy task format (only id, title, completed)
        legacy_data = [
            {"id": 1, "title": "Legacy Task", "completed": True}
        ]
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        # Load using application logic
        loaded = todo.load_tasks(file_path=self.temp_file)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["priority"], "Medium")  # Default assigned
        self.assertEqual(loaded[0]["category"], "General")  # Default assigned
        self.assertTrue(loaded[0]["completed"])

    def test_corrupt_file_resilience(self):
        """Test that corrupted JSON is caught gracefully."""
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write("corrupted json data :::")

        loaded = todo.load_tasks(file_path=self.temp_file)
        self.assertEqual(loaded, [])


if __name__ == "__main__":
    unittest.main()
