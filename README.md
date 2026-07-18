
# tsu-todo

`tsu-todo` is a small command-line to-do manager for tracking tasks from the terminal. It supports adding tasks, marking tasks as complete, deadlines, important flags, and a Rich-powered table view.

> [!IMPORTANT]
> This project is under active development. The current command set is intentionally small.

## Features

- Add tasks with optional deadlines and importance markers.
- List open tasks in a formatted terminal table.
- Automatically marks past deadlines as overdue.
- Complete a task by ID and remove it from the active list.
- Stores task data locally in a permanent, centralized `tasks.json` directory.

## Requirements

- Python `3.10` or newer
- [`uv`](https://docs.astral.sh/uv/) for dependency management and command execution

## Dependencies

Runtime dependencies are defined in `pyproject.toml`, but this project only uses two dependencies:

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
todo
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

To protect your todo items from being accidentally deleted during application updates or uninstalls, `tsu-todo` avoids using relative execution paths. Instead, your tasks are securely anchored inside your operating system's permanent local data directory:

- **Linux / WSL:** `~/.local/share/tsutodo/tasks.json`
- **macOS:** `~/Library/Application Support/tsutodo/tasks.json`
- **Windows:** `%LOCALAPPDATA%\tsutodo\tasks.json` or `C:\Users\YourName\AppData\Local\tsutodo\tasks.json`

This centralized design ensures you can view and update the exact same task list regardless of which directory your terminal is currently sitting in.

## Development

Run the test suite:

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
