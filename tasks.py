from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Self

import storage


class TaskNotFoundError(Exception):
    """raised when an id doesn't match any task in the list"""

    pass


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    deadline: str | None = None
    important: bool = False
    time_created: str = field(default_factory=lambda: datetime.now().isoformat())
    overdue: bool = False

    def __post_init__(self) -> None:
        """Computes the overdue state automatically"""
        if not self.deadline:
            self.overdue = False
            return

        try:
            try:
                deadline_dt = datetime.fromisoformat(self.deadline)
                self.overdue = datetime.now() > deadline_dt
            except ValueError:
                deadline_date = datetime.fromisoformat(self.deadline)
                self.overdue = datetime.today() > deadline_date
        except ValueError:
            self.overdue = False

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Turns a single dict to a Task object"""
        valid_fields: dict = {
            k: v for k, v in data.items() if k in cls.__dataclass_fields__
        }

        if "id" in valid_fields:
            valid_fields["id"] = int(valid_fields["id"])
        if "title" in valid_fields:
            valid_fields["title"] = str(valid_fields["title"])

        return cls(**valid_fields)


def tasks_to_dicts(tasks: list[Task]) -> list[dict[str, Any]]:
    """Transforms a collection of live Tasks to pure data structures for storage."""
    return [asdict(task) for task in tasks]


def dicts_to_tasks(dicts: list[dict[str, Any]]) -> list[Task]:
    """Hydrates a collection of raw storage items into rich domain Task objects."""
    return [Task.from_dict(d) for d in dicts]


# Combination (or Pipeline) of those two helpers above
def _get_task_sort_key(task: Task) -> tuple[int, str, int, int]:
    """
    Private sorting key shared by loading and saving operations.

    Groups by deadline presence, sorts chronologically, breaks ties
    with importance, and falls back to the original task ID.
    """
    # 1. Tasks with deadlines (0) go above open-ended N/A tasks (1)
    has_no_deadline = 1 if task.deadline is None else 0

    # 2. Chronological date string comparison (N/A slides out to year 9999)
    deadline_str = task.deadline if task.deadline is not None else "9999-12-31"

    # 3. Important (0) bubbles up higher than unimportant (1)
    is_not_important = 0 if task.important else 1

    return (has_no_deadline, deadline_str, is_not_important, task.id)


def load_task_objects() -> list[Task]:
    """Loads, hydrates, and ranks tasks dynamically based on chronological priority."""
    raw_dicts = storage.load_tasks()
    unordered_tasks = dicts_to_tasks(raw_dicts)
    return sorted(unordered_tasks, key=_get_task_sort_key)


def save_task_objects(tasks: list[Task]) -> None:
    """
    Sorts, re-indexes IDs sequentially from 1 to N, and saves task data safely.
    """
    # Sort the array using the shared top-level criteria helper
    sorted_tasks = sorted(tasks, key=_get_task_sort_key)

    # Mutate the IDs sequentially based on the clean sorted order
    for new_id, task in enumerate(sorted_tasks, start=1):
        task.id = new_id

    # Serialize and commit through the atomic storage layer
    raw_dicts = tasks_to_dicts(sorted_tasks)
    storage.save_tasks(raw_dicts)


def _find_task_by_id(tasks: list[Task], task_id: int) -> Task | None:
    """Private locator helper"""
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def mark_done(tasks: list[Task], task_id: int) -> None:
    """Locates and mark a task as done, raises the TaskNotFoundError if cannot find the task"""
    task: Task | None = _find_task_by_id(tasks, task_id)
    if not task:
        raise TaskNotFoundError(f"No task found with ID: {task_id}")
    task.done = True


def _is_valid_datetime_format(deadline_str: str) -> bool:
    """Helper to check the YYYY-MM-DD format"""
    try:
        date.fromisoformat(deadline_str)
        return True
    except ValueError:
        try:
            datetime.fromisoformat(deadline_str)
            return True
        except ValueError:
            return False


def create_task(
    tasks: list[Task], title: str, deadline: str | None = None, important: bool = False
) -> Task:
    """
    Creates, appends, and returns a new Task instance.

    Generates IDs using a gap-reuse strategy (finding the lowest available
    positive integer starting from 1).
    """
    if deadline is not None and not _is_valid_datetime_format(deadline):
        raise ValueError("Invalid datetime format. Please use YYYY-MM-DD")

    existing_id: set[int] = {task.id for task in tasks}
    next_id: int = 1
    while next_id in existing_id:
        next_id += 1

    new_task: Task = Task(
        id=next_id, title=title, deadline=deadline, important=important
    )

    tasks.append(new_task)
    return new_task
