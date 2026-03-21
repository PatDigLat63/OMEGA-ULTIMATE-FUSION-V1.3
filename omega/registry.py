"""Module registry – discovers and manages all available OMEGA modules."""

from __future__ import annotations

import importlib
import pkgutil
from typing import Dict, Type

from omega.modules.base import BaseModule


class ModuleRegistry:
    """Discovers and stores all BaseModule subclasses found in omega.modules."""

    def __init__(self) -> None:
        self._modules: Dict[str, Type[BaseModule]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover(self) -> None:
        """Import every sub-module inside *omega.modules* and register its
        BaseModule subclasses automatically."""
        import omega.modules as pkg

        for finder, module_name, _ispkg in pkgutil.iter_modules(pkg.__path__):
            full_name = f"omega.modules.{module_name}"
            importlib.import_module(full_name)

        # Collect all concrete subclasses
        for cls in BaseModule.__subclasses__():
            self._modules[cls.name] = cls

    def get(self, name: str) -> Type[BaseModule] | None:
        return self._modules.get(name)

    def all(self) -> Dict[str, Type[BaseModule]]:
        return dict(self._modules)

    def names(self) -> list[str]:
        return sorted(self._modules.keys())
