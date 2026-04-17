"""Core fusion engine – orchestrates module discovery and execution."""

from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, List, Optional

from omega.registry import ModuleRegistry

logger = logging.getLogger(__name__)


class FusionEngine:
    """Central orchestrator for the OMEGA command hub.

    Responsibilities
    ----------------
    * Discovers all registered modules via :class:`~omega.registry.ModuleRegistry`.
    * Maintains a simple audit log of every command executed.
    * Provides a high-level ``execute`` API for running any module by name.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self.registry = ModuleRegistry()
        self._audit_log: List[Dict[str, Any]] = []
        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Discover all modules and prepare the engine."""
        if self._initialized:
            return
        self.registry.discover()
        self._initialized = True
        logger.info("FusionEngine initialized – %d modules loaded.", len(self.registry.all()))

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, module_name: str, module_config: Optional[Dict[str, Any]] = None) -> None:
        """Instantiate and run *module_name* with an optional config override."""
        if not self._initialized:
            self.initialize()

        cls = self.registry.get(module_name)
        if cls is None:
            raise ValueError(f"Unknown module: '{module_name}'")

        merged_config = {**self.config, **(module_config or {})}
        instance = cls(config=merged_config)

        entry: Dict[str, Any] = {
            "module": module_name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "pending",
        }
        self._audit_log.append(entry)

        try:
            instance.run()
            entry["status"] = "success"
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
            logger.error("Module '%s' raised an error: %s", module_name, exc)
            raise

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def module_names(self) -> List[str]:
        """Return sorted list of available module names."""
        if not self._initialized:
            self.initialize()
        return self.registry.names()

    def audit_log(self) -> List[Dict[str, Any]]:
        """Return a copy of the execution audit log."""
        return list(self._audit_log)
