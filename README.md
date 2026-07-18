# tsutodo

`tsutodo` is a small command-line to-do manager for tracking tasks from the terminal. It supports adding tasks, marking tasks as complete, deadlines, important flags, and a Rich-powered table view.

## Notes

This project is under active development. The current command set is intentionally small: add, list, and complete tasks.

## Features

- Add tasks with optional deadlines and importance markers.
- List open tasks in a formatted terminal table.
- Automatically marks past deadlines as overdue.
- Complete a task by ID and remove it from the active list.
- Stores task data locally in `tasks.json`.

## Requirements

- Python `3.14` or newer
- [`uv`](https://docs.astral.sh/uv/) for dependency management and command execution

## Dependencies

Runtime dependencies are defined in `pyproject.toml`:

- `click` - CLI commands and argument parsing
- `rich` - formatted terminal output

The pinned dependency graph is stored in `uv.lock`.

## Installation

Install the CLI directly from GitHub with `uv`:

```bash
uv tool install git+https://github.com/tsuyoshi64/tsu-todo.git
```

Update an existing installation:

```bash
uv tool install git+https://github.com/tsuyoshi64/tsu-todo.git --upgrade
```

Verify the CLI is available:

```bash
todo --help
```

## Usage

### Add a task

```bash
todo add "Write project README"
```

Add a deadline:

```bash
todo add "Submit report" --deadline 2026-12-31
```

Mark a task as important:

```bash
todo add "Pay invoice" --important
```

Short flags are also available:

```bash
todo add "Book appointment" -d 2026-12-31 -i
```

### List tasks

```bash
todo list
```

The list view shows each task's ID, title, deadline, overdue status, and importance marker.

### Complete a task

```bash
todo done 1
```

Completed tasks are removed from the active task list.

## Data Storage

Tasks are saved to a local `tasks.json` file in the directory where the CLI is run. The file is ignored by Git so local task data is not committed to the repository.

Writes use a temporary file and `os.replace()` to reduce the chance of corrupting `tasks.json` during save operations.

## Development

Run the test suite:

```bash
uv run python -m unittest discover tests -v
```

Or use the included shell script:

```bash
./test.sh
```

## Project Structure

```text
.
|-- main.py             # Click CLI commands
|-- tasks.py            # Task model and task operations
|-- storage.py          # JSON load/save helpers
|-- tests/              # Unit tests
|-- pyproject.toml      # Project metadata and dependencies
|-- uv.lock             # Locked dependency versions
`-- README.md
```
