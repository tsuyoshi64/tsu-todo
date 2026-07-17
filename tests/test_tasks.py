import unittest
from datetime import datetime

from tasks import (
    Task,
    TaskNotFoundError,
    _find_task_by_id,
    create_task,
    dicts_to_tasks,
    mark_done,
    tasks_to_dicts,
)


class TestTasksModule(unittest.TestCase):
    # 1. TEST CUSTOM EXCEPTION & DATACLASS DEFAULTS
    def test_task_not_found_error_inheritance(self) -> None:
        """Verify TaskNotFoundError behaves as a proper Exception subclass."""
        err = TaskNotFoundError("Test error message")
        self.assertIsInstance(err, Exception)
        self.assertEqual(str(err), "Test error message")

    def test_task_dataclass_default_instantiation(self) -> None:
        """Verify fallback behavior for omitted properties on standard tasks."""
        task = Task(id=1, title="Mow the lawn")

        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Mow the lawn")
        self.assertFalse(task.done)
        self.assertFalse(task.important)
        self.assertIsNone(task.deadline)

        # Ensure time_created is valid ISO 8601 string format
        try:
            datetime.fromisoformat(task.time_created)
        except ValueError:
            self.fail("time_created property failed to provide a valid ISO 8601 string.")

    # 2. TEST SERIALIZATION / DESERIALIZATION PIPELINE
    def test_task_from_dict_happy_path(self) -> None:
        """Verify raw dictionary deserialization maps all fields correctly."""
        raw = {
            "id": 10,
            "title": "Clean keyboard",
            "done": True,
            "deadline": "2026-07-20",
            "important": True,
            "time_created": "2026-07-17T12:00:00",
        }
        task = Task.from_dict(raw)

        self.assertEqual(task.id, 10)
        self.assertEqual(task.title, "Clean keyboard")
        self.assertTrue(task.done)
        self.assertTrue(task.important)
        self.assertEqual(task.deadline, "2026-07-20")
        self.assertEqual(task.time_created, "2026-07-17T12:00:00")

    def test_task_from_dict_schema_drift(self) -> None:
        """Verify extra unexpected dictionary fields are safely thrown out."""
        raw = {
            "id": 12,
            "title": "Buy groceries",
            "future_v3_flag": "ignored_value",
            "tags": ["personal", "urgent"],
        }
        task = Task.from_dict(raw)

        self.assertEqual(task.id, 12)
        self.assertEqual(task.title, "Buy groceries")
        self.assertFalse(hasattr(task, "future_v3_flag"))
        self.assertFalse(hasattr(task, "tags"))

    def test_tasks_to_dicts_mapping(self) -> None:
        """Verify automated serialization maps list objects down to dictionaries."""
        t1 = Task(id=1, title="Task One", done=True)
        t2 = Task(id=2, title="Task Two", important=True)

        raw_list = tasks_to_dicts([t1, t2])

        self.assertEqual(len(raw_list), 2)
        self.assertEqual(raw_list[0]["id"], 1)
        self.assertTrue(raw_list[0]["done"])
        self.assertEqual(raw_list[1]["id"], 2)
        self.assertTrue(raw_list[1]["important"])

    def test_dicts_to_tasks_mapping(self) -> None:
        """Verify batch list conversions rehydrate dictionaries into strict objects."""
        raw_dicts = [{"id": 1, "title": "A"}, {"id": 2, "title": "B"}]
        task_list = dicts_to_tasks(raw_dicts)

        self.assertEqual(len(task_list), 2)
        self.assertIsInstance(task_list[0], Task)
        self.assertEqual(task_list[0].title, "A")
        self.assertIsInstance(task_list[1], Task)
        self.assertEqual(task_list[1].title, "B")

    # 3. TEST PRIVATE HELPER & WORKFLOW MUTATIONS
    def test_find_task_by_id_scenarios(self) -> None:
        """Test matching and missing search targets through the internal index helper."""
        tasks = [Task(id=5, title="Five"), Task(id=10, title="Ten")]

        # Match Scenario
        found = _find_task_by_id(tasks, 10)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Ten")  # type: ignore

        # Miss Scenario
        missing = _find_task_by_id(tasks, 99)
        self.assertIsNone(missing)

    def test_mark_done_success(self) -> None:
        """Verify execution flow finds and flips state properties correctly."""
        tasks = [Task(id=1, title="Incomplete task", done=False)]

        mark_done(tasks, 1)
        self.assertTrue(tasks[0].done)

    def test_mark_done_failure_raises_not_found(self) -> None:
        """Verify operations on missing indexes fail predictably with TaskNotFoundError."""
        tasks = [Task(id=1, title="Test", done=False)]

        with self.assertRaises(TaskNotFoundError):
            mark_done(tasks, 404)

    # 4. TEST CORE FACTORY & ID GENERATION STRATEGY
    def test_create_task_appends_to_list(self) -> None:
        """Verify factory populates tracking list and maps explicit parameters."""
        task_list: list[Task] = []
        new_task = create_task(
            task_list, "My Task", deadline="2026-08-01", important=True
        )

        self.assertEqual(len(task_list), 1)
        self.assertIs(task_list[0], new_task)
        self.assertEqual(new_task.title, "My Task")
        self.assertEqual(new_task.deadline, "2026-08-01")
        self.assertTrue(new_task.important)

    def test_create_task_id_generation_empty(self) -> None:
        """Verify initial run maps default task ID to 1 when tracking index is clean."""
        task_list: list[Task] = []
        t = create_task(task_list, "First Task")
        self.assertEqual(t.id, 1)

    def test_create_task_id_generation_incremental(self) -> None:
        """Verify indices count upwards sequentially without manual input."""
        task_list = [Task(id=1, title="A"), Task(id=2, title="B")]
        t = create_task(task_list, "C")
        self.assertEqual(t.id, 3)

    def test_create_task_id_generation_gap_reuse_middle(self) -> None:
        """Verify gap-reuse strategy recycles deleted tracking indices cleanly."""
        # Gap exists at ID 2
        task_list = [Task(id=1, title="A"), Task(id=3, title="C")]
        t = create_task(task_list, "B")
        self.assertEqual(t.id, 2)

    def test_create_task_id_generation_gap_reuse_start(self) -> None:
        """Verify gap-reuse strategy recycles ID 1 if it becomes missing."""
        # Gap exists at the very beginning (ID 1)
        task_list = [Task(id=2, title="B"), Task(id=3, title="C")]
        t = create_task(task_list, "A")
        self.assertEqual(t.id, 1)


if __name__ == "__main__":
    unittest.main()
