import json
import os


def load_tasks(file_path: str = "tasks.json") -> list:
    """
    Loads raw task data from tasks.json.

    Handles missing json file, empty file by empty list.
    """
    if not os.path.exists(file_path):
        return []

    if os.path.getsize(file_path) == 0:
        return []

    with open(file_path, "r") as tasks_json:
        data = json.load(tasks_json)
        if not isinstance(data, list):
            raise ValueError("Malformed storage data: root element must be a list.")
        return data


def save_tasks(tasks: list, file_path="tasks.json") -> None:
    """
    Saves task data back to json file safety (I hope so).

    I'm using atomic-write pattern (temp & os.replace) to prevent torn writes.
    Does not validate task shapes or meanings, only acts as a byte/file manager.
    """
    tmp_path: str = f"{file_path}.tmp"

    try:
        with open(tmp_path, "w") as task_json:
            json.dump(tasks, task_json, indent=4)
            task_json.flush()
            os.fsync(task_json.fileno())
        os.replace(tmp_path, file_path)

    except:
        if os.path.isfile(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise
