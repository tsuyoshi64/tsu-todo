import json
import os
import platform


def _get_default_db_path() -> str:
    """
    Returns a centralized, cross-platform path for permanent storage.

    Guarantees user data survival during application uninstalls or upgrades.
    """
    if platform.system() == "Windows":
        base_dir = os.environ.get(
            "LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")
        )
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:  # Linux and other platforms
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))

    # Isolate within a dedicated project directory structure
    app_dir = os.path.join(base_dir, "tsutodo")
    os.makedirs(app_dir, exist_ok=True)

    file_path = os.path.join(app_dir, "tasks.json")

    if not os.path.exists(file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
        except OSError:
            pass

    return file_path


DEFAULT_DB_PATH = _get_default_db_path()


def load_tasks(file_path: str = DEFAULT_DB_PATH) -> list:
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


def save_tasks(tasks: list, file_path: str = DEFAULT_DB_PATH) -> None:
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
