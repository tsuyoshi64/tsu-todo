import click
from rich.console import Console
from rich.table import Table

import tasks

console = Console()


@click.group()
def cli() -> None:
    pass


@cli.command("list")
def list_tasks() -> None:
    """Displays all current tasks in an elegant, structured table."""
    try:
        task_list = tasks.load_task_objects()
    except Exception as e:
        console.print(f"[bold red]Storage Error:[/bold red] Could not load data. ({e})")
        return

    # Early exit if collection is empty
    if not task_list:
        console.print("[yellow]No tasks yet. You are completely free![/yellow]")
        return

    # Construct presentation table layout via Rich
    table = Table(title="Your To-Do List", title_style="bold cyan")
    table.add_column("ID", justify="right", style="dim", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Done", justify="center")
    table.add_column("Deadline", justify="center", style="magenta")
    table.add_column("Important", justify="center")

    # Hydrate rows applying visual conditional status iconography rules
    for task in task_list:
        status_icon = "[green]✓[/green]" if task.done else "[red]✗[/red]"
        importance_icon = (
            "[bold yellow]★[/bold yellow]" if task.important else "[dim]☆[/dim]"
        )
        deadline_text = task.deadline if task.deadline else "[dim]N/A[/dim]"

        table.add_row(
            str(task.id), task.title, status_icon, deadline_text, importance_icon
        )

    console.print(table)


@cli.command("add")
@click.argument("title", type=str)
@click.option(
    "--deadline",
    "-d",
    type=str,
    default=None,
    help="Optional deadline string (e.g., YYYY-MM-DD)",
)
@click.option(
    "--important", "-i", is_flag=True, help="Mark the task as highly important."
)
def add(title: str, deadline: str | None, important: bool) -> None:
    """Creates a new entry and commits it directly down to storage."""
    try:
        task_list = tasks.load_task_objects()

        # Core utility factory appends to the passed list array implicitly
        new_task = tasks.create_task(
            tasks=task_list, title=title, deadline=deadline, important=important
        )

        tasks.save_task_objects(task_list)
        console.print(
            f"[green]✓[/green] Added task [bold cyan]#{new_task.id}[/bold cyan]: {new_task.title}"
        )

    except Exception as e:
        console.print(f"[bold red]System Error:[/bold red] Operation failed. ({e})")


@cli.command("done")
@click.argument("task_id", type=int)
def done(task_id: int) -> None:
    try:
        task_list = tasks.load_task_objects()
    except Exception as e:
        console.print(f"[bold red]Storage Error:[/bold red] Could not load data. ({e})")
        return

    try:
        tasks.mark_done(task_list, task_id)
        task_to_remove = tasks._find_task_by_id(task_list, task_id)
        if task_to_remove:
            task_list.remove(task_to_remove)

    except tasks.TaskNotFoundError:
        console.print(
            f"[bold red]Error:[/bold red] Task ID [bold yellow]#{task_id}[/bold yellow] does not exist."
        )
        return

    try:
        tasks.save_task_objects(task_list)
        console.print(
            f"[green]✓[/green] Task [bold cyan]#{task_id}[/bold cyan] completed and automatically removed."
        )
    except Exception as e:
        console.print(
            f"[bold red]Storage Error:[/bold red] Could not save updated state. ({e})"
        )


if __name__ == "__main__":
    cli()
