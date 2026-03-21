"""Unit tests for the OMEGA core, registry, and modules."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from omega.core import FusionEngine
from omega.modules.base import BaseModule
from omega.registry import ModuleRegistry


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

class _DummyModule(BaseModule):
    name = "dummy"
    description = "A throwaway module used in tests"
    ran = False

    def run(self) -> None:
        _DummyModule.ran = True


# ---------------------------------------------------------------------------
# BaseModule
# ---------------------------------------------------------------------------

class TestBaseModule:
    def test_str_representation(self) -> None:
        m = _DummyModule()
        assert m.name in str(m)
        assert m.description in str(m)

    def test_config_defaults_to_empty_dict(self) -> None:
        m = _DummyModule()
        assert m.config == {}

    def test_config_is_stored(self) -> None:
        m = _DummyModule(config={"key": "value"})
        assert m.config["key"] == "value"

    def test_run_executes(self) -> None:
        _DummyModule.ran = False
        m = _DummyModule()
        m.run()
        assert _DummyModule.ran


# ---------------------------------------------------------------------------
# ModuleRegistry
# ---------------------------------------------------------------------------

class TestModuleRegistry:
    def test_discover_finds_builtin_modules(self) -> None:
        registry = ModuleRegistry()
        registry.discover()
        names = registry.names()
        assert "system-info" in names
        assert "task-runner" in names
        assert "config-manager" in names
        assert "logger" in names
        assert "scheduler" in names

    def test_get_returns_correct_class(self) -> None:
        from omega.modules.system_info import SystemInfoModule

        registry = ModuleRegistry()
        registry.discover()
        cls = registry.get("system-info")
        assert cls is SystemInfoModule

    def test_get_unknown_returns_none(self) -> None:
        registry = ModuleRegistry()
        registry.discover()
        assert registry.get("does-not-exist") is None

    def test_all_returns_dict_copy(self) -> None:
        registry = ModuleRegistry()
        registry.discover()
        all1 = registry.all()
        all2 = registry.all()
        assert all1 == all2
        # Mutations should not affect the internal state
        all1.clear()
        assert len(registry.all()) > 0


# ---------------------------------------------------------------------------
# FusionEngine
# ---------------------------------------------------------------------------

class TestFusionEngine:
    def test_initialize_loads_modules(self) -> None:
        engine = FusionEngine()
        engine.initialize()
        assert len(engine.module_names()) >= 5

    def test_initialize_is_idempotent(self) -> None:
        engine = FusionEngine()
        engine.initialize()
        engine.initialize()  # second call must not raise
        assert len(engine.module_names()) >= 5

    def test_execute_unknown_module_raises(self) -> None:
        engine = FusionEngine()
        engine.initialize()
        with pytest.raises(ValueError, match="Unknown module"):
            engine.execute("nonexistent")

    def test_execute_records_audit_entry(self) -> None:
        engine = FusionEngine()
        engine.initialize()
        # Patch system-info's run so we don't need real psutil data
        with patch("omega.modules.system_info.SystemInfoModule.run"):
            engine.execute("system-info")
        log = engine.audit_log()
        assert len(log) == 1
        assert log[0]["module"] == "system-info"
        assert log[0]["status"] == "success"

    def test_audit_log_returns_copy(self) -> None:
        engine = FusionEngine()
        engine.initialize()
        log1 = engine.audit_log()
        log1.append({"fake": True})
        assert len(engine.audit_log()) == 0  # original unaffected

    def test_execute_records_error_status(self) -> None:
        engine = FusionEngine()
        engine.initialize()

        with patch("omega.modules.system_info.SystemInfoModule.run", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                engine.execute("system-info")

        log = engine.audit_log()
        assert log[0]["status"] == "error"
        assert "boom" in log[0]["error"]

    def test_config_passed_to_module(self) -> None:
        engine = FusionEngine(config={"timeout": 99})
        engine.initialize()

        captured: Dict[str, Any] = {}

        def _capture_run(self_inner: BaseModule) -> None:
            captured.update(self_inner.config)

        with patch("omega.modules.task_runner.TaskRunnerModule.run", _capture_run):
            engine.execute("task-runner")

        assert captured.get("timeout") == 99


# ---------------------------------------------------------------------------
# ConfigManagerModule helpers (static methods)
# ---------------------------------------------------------------------------

class TestConfigManagerStatics:
    def test_load_nonexistent_returns_empty(self) -> None:
        from omega.modules.config_manager import ConfigManagerModule

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nope.json"
            data = ConfigManagerModule._load(path)
            assert data == {}

    def test_save_and_load_roundtrip(self) -> None:
        from omega.modules.config_manager import ConfigManagerModule

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cfg.json"
            original = {"alpha": 1, "beta": [1, 2, 3]}
            ConfigManagerModule._save(path, original)
            loaded = ConfigManagerModule._load(path)
            assert loaded == original

    def test_load_invalid_json_returns_empty(self) -> None:
        from omega.modules.config_manager import ConfigManagerModule

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{{not valid json", encoding="utf-8")
            data = ConfigManagerModule._load(path)
            assert data == {}


# ---------------------------------------------------------------------------
# SystemInfoModule
# ---------------------------------------------------------------------------

class TestSystemInfoModule:
    def test_run_does_not_raise(self) -> None:
        from omega.modules.system_info import SystemInfoModule

        # Just verify it runs without crashing (uses real psutil).
        m = SystemInfoModule()
        m.run()

    def test_fmt_bytes(self) -> None:
        from omega.modules.system_info import _fmt_bytes

        assert _fmt_bytes(0) == "0.00 B"
        assert "KB" in _fmt_bytes(2048)
        assert "MB" in _fmt_bytes(2 * 1024 * 1024)
        assert "GB" in _fmt_bytes(2 * 1024 ** 3)
