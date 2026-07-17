from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Self


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


def create_task(
    tasks: list[Task], title: str, deadline: str | None = None, important: bool = False
) -> Task:
    """
    Creates, appends, and returns a new Task instance.

    Generates IDs using a gap-reuse strategy (finding the lowest available
    positive integer starting from 1).
    """
    existing_id: set[int] = {task.id for task in tasks}
    next_id: int = 1
    while next_id in existing_id:
        next_id += 1

    new_task: Task = Task(
        id=next_id, title=title, deadline=deadline, important=important
    )

    tasks.append(new_task)
    return new_task
