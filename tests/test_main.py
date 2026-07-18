import unittest
from unittest.mock import patch

from click.testing import CliRunner

# Import the main CLI and custom domain exceptions
from main import cli
from tasks import Task, TaskNotFoundError


class TestMainCLI(unittest.TestCase):
    def setUp(self) -> None:
        """Initialize the Click execution runner framework."""
        self.runner = CliRunner()

    # 1. LIST
    @patch("main.tasks.load_task_objects")
    def test_list_command_empty_state(self, mock_load) -> None:
        """Verify the system handles empty collections with a friendly status warning."""
        mock_load.return_value = []

        result = self.runner.invoke(cli, ["list"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("No tasks yet", result.output)
        mock_load.assert_called_once()

    @patch("main.tasks.load_task_objects")
    def test_list_command_with_records(self, mock_load) -> None:
        """Verify list command draws a structured matrix showing all record properties."""
        mock_load.return_value = [
            Task(
                id=1, title="Task A", done=False, deadline="2026-12-01", important=True
            ),
            Task(id=2, title="Task B", done=True, deadline=None, important=False),
        ]

        result = self.runner.invoke(cli, ["list"])

        self.assertEqual(result.exit_code, 0)
        # Check table structural presence columns disregarding formatting tags
        self.assertIn("ID", result.output)
        self.assertIn("Title", result.output)
        self.assertIn("Task A", result.output)
        self.assertIn("2026-12-01", result.output)
        self.assertIn("Task B", result.output)

    @patch("main.tasks.load_task_objects")
    def test_list_command_handles_corrupted_storage_fault(self, mock_load) -> None:
        """Verify system structural exceptions are caught safely without a hard terminal crash."""
        mock_load.side_effect = Exception("Disk read crash simulated")

        result = self.runner.invoke(cli, ["list"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Storage Error:", result.output)

    # 2. ADD
    @patch("main.tasks.save_task_objects")
    @patch("main.tasks.create_task")
    @patch("main.tasks.load_task_objects")
    def test_add_command_happy_path(self, mock_load, mock_create, mock_save) -> None:
        """Verify basic additions call mutations and execute pipeline saving cascades."""
        mock_load.return_value = []
        mock_create.return_value = Task(id=1, title="Mow Lawn")

        result = self.runner.invoke(cli, ["add", "Mow Lawn"])

        self.assertEqual(result.exit_code, 0)
        # Assert structural text match while stripping/ignoring style sequences
        self.assertIn("Added task", result.output)
        self.assertIn("1", result.output)
        self.assertIn("Mow Lawn", result.output)

        mock_load.assert_called_once()
        mock_create.assert_called_once_with(
            tasks=[], title="Mow Lawn", deadline=None, important=False
        )
        mock_save.assert_called_once()

    @patch("main.tasks.save_task_objects")
    @patch("main.tasks.create_task")
    @patch("main.tasks.load_task_objects")
    def test_add_command_with_optional_flags(
        self, mock_load, mock_create, mock_save
    ) -> None:
        """Verify CLI safely extracts optional parameter flags down to the model creator."""
        mock_load.return_value = []
        mock_create.return_value = Task(
            id=5, title="Submit Paper", deadline="2026-05-01", important=True
        )

        result = self.runner.invoke(
            cli, ["add", "Submit Paper", "-d", "2026-05-01", "-i"]
        )

        self.assertEqual(result.exit_code, 0)
        mock_create.assert_called_once_with(
            tasks=[], title="Submit Paper", deadline="2026-05-01", important=True
        )

    # 3. DONE
    @patch("main.tasks.save_task_objects")
    @patch("main.tasks.mark_done")
    @patch("main.tasks.load_task_objects")
    def test_done_command_success_pipeline(
        self, mock_load, mock_mark, mock_save
    ) -> None:
        """Verify successful completions match, mutate, remove from list, and save."""
        # Create a real list so the .remove() operation doesn't crash on a mock
        target_task = Task(id=3, title="Fix plumbing")
        mock_list = [target_task]
        mock_load.return_value = mock_list

        result = self.runner.invoke(cli, ["done", "3"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("completed and automatically removed", result.output)
        self.assertIn("3", result.output)

        mock_mark.assert_called_once_with(mock_list, 3)
        # Verify it saves an empty array because the single item was dropped cleanly
        mock_save.assert_called_once_with([])

    @patch("main.tasks.save_task_objects")
    @patch("main.tasks.mark_done")
    @patch("main.tasks.load_task_objects")
    def test_done_command_missing_id_aborts_save(
        self, mock_load, mock_mark, mock_save
    ) -> None:
        """Verify missing ID selections log clean warnings and skip disk serialization steps."""
        mock_list = [Task(id=1, title="Empty")]
        mock_load.return_value = mock_list
        mock_mark.side_effect = TaskNotFoundError("Not found")

        result = self.runner.invoke(cli, ["done", "99"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Task ID", result.output)
        self.assertIn("99", result.output)
        self.assertIn("does not exist", result.output)
        mock_save.assert_not_called()

    def test_done_command_invalid_argument_type(self) -> None:
        """Verify Click intercepts invalid alphabetic string inputs for integer ID inputs."""
        result = self.runner.invoke(cli, ["done", "not-an-integer"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Error: Invalid value for 'TASK_ID'", result.output)


if __name__ == "__main__":
    unittest.main()
