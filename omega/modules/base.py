"""Base class that every OMEGA module must extend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModule(ABC):
    """Abstract base for all OMEGA capability modules.

    Subclasses must set the class-level ``name`` and ``description``
    attributes and implement :meth:`run`.
    """

    #: Unique short identifier used in the registry and CLI menu.
    name: str = ""
    #: One-line human-readable description shown in the hub menu.
    description: str = ""

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    def run(self) -> None:
        """Execute the module's primary function."""

    def __str__(self) -> str:
        return f"[{self.name}] {self.description}"
