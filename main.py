#!/usr/bin/env python3
"""OMEGA-ULTIMATE-FUSION V1.3 – sovereign command hub entry point."""

from __future__ import annotations

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from omega import __version__
from omega.core import FusionEngine

console = Console()

# Configure root logger to write to file as well as stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

_BANNER = rf"""
  ___  __  __ _____ ____    _      _   _ _   _____ ___ __  __    _ _____ _____
 / _ \|  \/  | ____/ ___|  / \    | | | | | |_   _|_ _|  \/  |  / |_   _| ____|
| | | | |\/| |  _|| |  _  / _ \   | | | | |   | |  | || |\/| |  | | | | |  _|
| |_| | |  | | |__| |_| |/ ___ \  | |_| | |___| |  | || |  | |  | | | | | |___
 \___/|_|  |_|_____\____/_/   \_\  \___/|_____|_| |___|_|  |_|  |_| |_| |_____|

        F U S I O N   v{__version__}  –  Sovereign Command Hub  🔱
"""


def _print_banner() -> None:
    console.print(Panel.fit(Text(_BANNER, style="bold cyan"), border_style="cyan"))


def _build_menu(engine: FusionEngine) -> Table:
    """Render the module selection menu as a Rich table."""
    table = Table(show_header=True, header_style="bold magenta", border_style="magenta")
    table.add_column("#", style="bold", width=4)
    table.add_column("Module", style="bold cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for idx, name in enumerate(engine.module_names(), start=1):
        cls = engine.registry.get(name)
        desc = cls.description if cls else ""
        table.add_row(str(idx), name, desc)

    return table


def run(config: Optional[dict] = None) -> None:
    """Start the interactive OMEGA command hub."""
    _print_banner()

    engine = FusionEngine(config=config)
    engine.initialize()

    module_names = engine.module_names()

    console.print(f"[bold green]✔  {len(module_names)} modules loaded and fused.[/bold green]\n")

    while True:
        console.print(_build_menu(engine))
        console.print("\n  [cyan]a[/cyan] = Audit log   [cyan]q[/cyan] = Quit\n")

        choices = [str(i) for i in range(1, len(module_names) + 1)] + ["a", "q"]
        choice = Prompt.ask("[bold yellow]Select module[/bold yellow]", choices=choices, show_choices=False)

        if choice == "q":
            console.print("[bold]Goodbye from OMEGA 🔱[/bold]")
            break
        elif choice == "a":
            _show_audit_log(engine)
        else:
            module_name = module_names[int(choice) - 1]
            console.print(f"\n[bold cyan]── {module_name} ──[/bold cyan]\n")
            try:
                engine.execute(module_name)
            except Exception as exc:  # noqa: BLE001
                console.print(f"[bold red]Error:[/bold red] {exc}")
            console.print()


def _show_audit_log(engine: FusionEngine) -> None:
    log = engine.audit_log()
    if not log:
        console.print("[dim]No commands executed yet.[/dim]\n")
        return

    table = Table(title="Audit Log", border_style="blue")
    table.add_column("Module", style="bold")
    table.add_column("Timestamp")
    table.add_column("Status")

    for entry in log:
        status_style = "green" if entry["status"] == "success" else ("yellow" if entry["status"] == "pending" else "red")
        table.add_row(
            entry["module"],
            entry["timestamp"],
            f"[{status_style}]{entry['status']}[/{status_style}]",
        )

    console.print(table)
    console.print()


if __name__ == "__main__":
    run()
