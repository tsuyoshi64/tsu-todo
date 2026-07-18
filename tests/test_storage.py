import json
import os
import unittest

from storage import load_tasks, save_tasks


class TestStorageModule(unittest.TestCase):
    def setUp(self) -> None:
        """Set up a distinct temporary file path for isolated testing."""
        self.test_file = "test_tasks.json"
        self.test_tmp_file = f"{self.test_file}.tmp"

    def tearDown(self) -> None:
        """Clean up any leftover files to prevent CI pollution."""
        for path in (self.test_file, self.test_tmp_file):
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    # load_tasks()
    def test_load_file_does_not_exist(self) -> None:
        """Scenario 1: Fresh install. File missing must return an empty list."""
        result = load_tasks(self.test_file)
        self.assertEqual(result, [])

    def test_load_file_exists_but_empty(self) -> None:
        """Scenario 2: File exists but is 0 bytes. Must return an empty list."""
        with open(self.test_file, "w") as f:
            pass

        result = load_tasks(self.test_file)
        self.assertEqual(result, [])

    def test_load_file_valid_json(self) -> None:
        """Happy Path: File contains a valid JSON task array."""
        mock_data = [{"id": 1, "title": "Buy milk", "done": False}]
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(mock_data, f)

        result = load_tasks(self.test_file)
        self.assertEqual(result, mock_data)

    def test_load_file_corrupted_json(self) -> None:
        """Scenario 3: Malformed JSON structure must propagate JSONDecodeError."""
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json string... ")

        with self.assertRaises(json.JSONDecodeError):
            load_tasks(self.test_file)

    def test_load_file_invalid_root_type(self) -> None:
        """Architecture Guard: Root elements that are dictionaries must fail."""
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump({"not_a_list": True}, f)

        with self.assertRaises(ValueError):
            load_tasks(self.test_file)

    # save_tasks()
    def test_save_tasks_successful_write(self) -> None:
        """Happy Path: Successfully saves data using the atomic pipeline."""
        mock_data = [{"id": 2, "title": "Read book", "done": True}]

        save_tasks(mock_data, self.test_file)

        self.assertTrue(os.path.isfile(self.test_file))
        with open(self.test_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data, mock_data)
        self.assertFalse(os.path.isfile(self.test_tmp_file))


if __name__ == "__main__":
    unittest.main()
