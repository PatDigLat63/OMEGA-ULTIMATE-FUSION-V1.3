"""Config-Manager module – view and edit the hub's JSON configuration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.pretty import pprint
from rich.prompt import Prompt

from omega.modules.base import BaseModule

console = Console()

DEFAULT_CONFIG_PATH = Path.home() / ".omega" / "config.json"


class ConfigManagerModule(BaseModule):
    """Manage the OMEGA hub configuration stored in ~/.omega/config.json."""

    name = "config-manager"
    description = "View and edit the hub's JSON configuration file"

    def run(self) -> None:
        config_path = Path(self.config.get("config_path", DEFAULT_CONFIG_PATH))
        config_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"[bold cyan]Config Manager[/bold cyan] – {config_path}\n")

        data = self._load(config_path)

        while True:
            console.print("[bold]Options:[/bold]")
            console.print("  [cyan]1[/cyan] View current config")
            console.print("  [cyan]2[/cyan] Set a key")
            console.print("  [cyan]3[/cyan] Delete a key")
            console.print("  [cyan]4[/cyan] Save and exit")
            console.print("  [cyan]q[/cyan] Exit without saving\n")

            choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "q"])

            if choice == "1":
                pprint(data)
            elif choice == "2":
                key = Prompt.ask("Key")
                value_str = Prompt.ask("Value (JSON)")
                try:
                    data[key] = json.loads(value_str)
                except json.JSONDecodeError:
                    data[key] = value_str
                console.print(f"[green]Set[/green] {key!r}.")
            elif choice == "3":
                key = Prompt.ask("Key to delete")
                if key in data:
                    del data[key]
                    console.print(f"[yellow]Deleted[/yellow] {key!r}.")
                else:
                    console.print(f"[red]Key {key!r} not found.[/red]")
            elif choice == "4":
                self._save(config_path, data)
                console.print(f"[green]Config saved to {config_path}[/green]")
                break
            elif choice == "q":
                break

            console.print()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load(path: Path) -> Dict[str, Any]:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                console.print("[yellow]Warning:[/yellow] Existing config is invalid JSON – starting fresh.")
        return {}

    @staticmethod
    def _save(path: Path, data: Dict[str, Any]) -> None:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
