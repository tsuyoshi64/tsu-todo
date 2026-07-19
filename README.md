
# tsu-todo

`tsu-todo` is a small command-line to-do manager for tracking tasks from the terminal. It supports adding tasks, marking tasks as complete, deadlines, important flags, and a Rich-powered table view.

> [!IMPORTANT]
> This project is under active development. The current command set is intentionally small.

## Features

- **Chronological Sorting Matrix:** Automatically forces your list to rank by closest deadlines, using importance status flags as identical date tie-breakers.
- **Sequential ID Auto-Update:** Re-indexes your internal database task identifiers dynamically from 1 to N during every single update loop so your ID table column always stays perfectly sorted and uniform.
- **Add Tasks Natively:** Easily assign clear titles, optional chronological deadlines, and importance markers.
- **Dynamic Overdue Tracking:** Flags past milestones immediately inside a stylized column layout.
- **Instant Purification Delete:** Purges entries directly out of your list array database whenever they are marked completed via the `done` workflow.
- **Persistent Data Shield:** Safely protects record files across a cross-platform system database path.

## Requirements

- Python `3.10` or newer
- [`uv`](https://docs.astral.sh/uv/) for dependency management and command execution

## Dependencies

Runtime dependencies are defined in `pyproject.toml`. This project values minimalism and strictly uses two external library packages:

- `click` - CLI commands, flag tracking, and input validation
- `rich` - Formatted console tabular grids and color matrices

The pinned dependency graph is stored in `uv.lock`.

## Installation

Install the CLI globally from GitHub with `uv`:

```bash
uv tool install git+https://github.com/tsuyoshi64/tsu-todo.git
```

Update an existing installation to pull down the newest changes:

```bash
uv tool install git+https://github.com/tsuyoshi64/tsu-todo.git --upgrade
```

Verify that the command entry point routing is configured on your path correctly:

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

Short flags are also available to use simultaneously:

```bash
todo add "Book appointment" -d 2026-12-31 -i
```

### List tasks

```bash
todo list
```

The list view draws an organized matrix showing each task's ID, title, deadline, overdue status, and importance marker. 

#### Sorting Rules:
1. Tasks **with deadlines** group at the top, ordered strictly from closest to farthest date.
2. If two tasks share the **exact same day**, the important one bubbles above the unimportant one.
3. Tasks **without deadlines** slide to the bottom, sorted by importance.

### Complete a task

```bash
todo done 1
```

Completed tasks are immediately removed from your active collection list, triggering an auto-reindex step that shifts remaining task IDs to match their visual placement order starting from `1`.

## Data Storage

To protect your todo items from being accidentally deleted during application updates or uninstalls, `tsu-todo` avoids using relative path folders. Instead, your tasks are securely anchored inside your operating system's permanent local data directory:

- **Linux / WSL:** `~/.local/share/tsutodo/tasks.json`
- **macOS:** `~/Library/Application Support/tsutodo/tasks.json`
- **Windows:** `%LOCALAPPDATA%\tsutodo\tasks.json` *(e.g., `C:\Users\YourUsername\AppData\Local\tsutodo\tasks.json`)*

This centralized design ensures you can view and update the exact same task list regardless of which directory your terminal is currently sitting in.

## Testing

Run the test suite across all modules simultaneously:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Or execute your shortcut shell runner script:

```bash
./test.sh
```

## Project Structure

```text
.
|-- main.py             # Click CLI commands and user messages
|-- tasks.py            # Task model, validation guards, and sorting matrix
|-- storage.py          # JSON load/save atomic handlers
|-- tests/              # Exhaustive test suites folder
|-- pyproject.toml      # Project packaging metadata and backend build anchors
|-- uv.lock             # Locked dependency version graphs
`-- README.md
```
