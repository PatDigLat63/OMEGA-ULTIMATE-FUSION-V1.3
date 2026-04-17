"""Scheduler module – manage and run periodic background tasks."""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Dict, List

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from omega.modules.base import BaseModule

console = Console()


class ScheduledTask:
    """Lightweight wrapper around a repeating job."""

    def __init__(self, name: str, interval_seconds: int, func: Callable[[], Any]) -> None:
        self.name = name
        self.interval = interval_seconds
        self.func = func
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.run_count = 0
        self.last_error: str | None = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name=f"omega-task-{self.name}")
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _loop(self) -> None:
        while not self._stop_event.wait(self.interval):
            try:
                self.func()
                self.run_count += 1
            except Exception as exc:  # noqa: BLE001
                self.last_error = str(exc)


class SchedulerModule(BaseModule):
    """Schedule and manage repeating background tasks."""

    name = "scheduler"
    description = "Create, list and control periodic background tasks"

    # Shared task registry across instances (singleton per process), guarded by a lock.
    _tasks: Dict[str, ScheduledTask] = {}
    _lock: threading.Lock = threading.Lock()

    def run(self) -> None:
        console.print("[bold cyan]Scheduler[/bold cyan] – manage periodic background tasks.\n")

        while True:
            console.print("[bold]Options:[/bold]")
            console.print("  [cyan]1[/cyan] List tasks")
            console.print("  [cyan]2[/cyan] Add demo task (prints a heartbeat)")
            console.print("  [cyan]3[/cyan] Stop a task")
            console.print("  [cyan]q[/cyan] Return to hub\n")

            choice = Prompt.ask("Choice", choices=["1", "2", "3", "q"])

            if choice == "1":
                self._list_tasks()
            elif choice == "2":
                self._add_demo_task()
            elif choice == "3":
                self._stop_task()
            elif choice == "q":
                break

            console.print()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _list_tasks(self) -> None:
        with self.__class__._lock:
            tasks = dict(self.__class__._tasks)

        if not tasks:
            console.print("[dim]No tasks registered.[/dim]")
            return

        table = Table(title="Scheduled Tasks", border_style="magenta")
        table.add_column("Name", style="bold")
        table.add_column("Interval (s)")
        table.add_column("Running?")
        table.add_column("Runs")
        table.add_column("Last Error")

        for task in tasks.values():
            running = "[green]Yes[/green]" if task.is_running() else "[red]No[/red]"
            table.add_row(
                task.name,
                str(task.interval),
                running,
                str(task.run_count),
                task.last_error or "-",
            )

        console.print(table)

    def _add_demo_task(self) -> None:
        name = Prompt.ask("Task name", default="heartbeat")
        interval = IntPrompt.ask("Interval (seconds)", default=10)

        def _heartbeat() -> None:
            console.print(f"[dim]♥ [{name}] heartbeat[/dim]")

        task = ScheduledTask(name=name, interval_seconds=interval, func=_heartbeat)
        task.start()
        with self.__class__._lock:
            self.__class__._tasks[name] = task
        console.print(f"[green]Task '{name}' started (every {interval}s).[/green]")

    def _stop_task(self) -> None:
        with self.__class__._lock:
            tasks = dict(self.__class__._tasks)

        if not tasks:
            console.print("[dim]No tasks to stop.[/dim]")
            return

        name = Prompt.ask("Task name to stop")
        with self.__class__._lock:
            task = self.__class__._tasks.get(name)
        if task is None:
            console.print(f"[red]Task '{name}' not found.[/red]")
            return

        task.stop()
        console.print(f"[yellow]Task '{name}' stopped.[/yellow]")
