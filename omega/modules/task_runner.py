"""Task-Runner module – execute shell commands and capture output."""

from __future__ import annotations

import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from omega.modules.base import BaseModule

console = Console()


class TaskRunnerModule(BaseModule):
    """Run arbitrary shell commands and display their output in a styled panel."""

    name = "task-runner"
    description = "Execute shell commands and capture / display their output"

    def run(self) -> None:
        console.print("[bold cyan]Task Runner[/bold cyan] – enter commands below.")
        console.print("Type [bold red]exit[/bold red] or [bold red]quit[/bold red] to return to the hub.\n")

        while True:
            cmd = Prompt.ask("[bold yellow]>[/bold yellow] Command")
            if cmd.strip().lower() in ("exit", "quit", ""):
                break
            self._execute(cmd)

    def _execute(self, cmd: str) -> None:
        try:
            result = subprocess.run(
                cmd,
                shell=True,  # noqa: S602
                capture_output=True,
                text=True,
                timeout=self.config.get("timeout", 30),
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if stdout:
                console.print(Panel(stdout, title="stdout", border_style="green"))
            if stderr:
                console.print(Panel(stderr, title="stderr", border_style="red"))
            if not stdout and not stderr:
                console.print(Text("(no output)", style="dim"))
        except subprocess.TimeoutExpired:
            console.print("[bold red]Error:[/bold red] Command timed out.")
        except Exception as exc:  # noqa: BLE001
            console.print(f"[bold red]Error:[/bold red] {exc}")
