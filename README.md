# OMEGA-ULTIMATE-FUSION V1.3 🔱

> The final synthesis. Every module fused into one sovereign command hub.
> Built with 4 months of relentless Brotherhood work. Total control, absolute power.

---

## Overview

OMEGA-ULTIMATE-FUSION V1.3 is a unified Python command hub that discovers, loads and
orchestrates a set of independent capability modules through a single interactive CLI.
Each module is a self-contained unit; the **FusionEngine** binds them all at runtime.

```
  OMEGA ULTIMATE FUSION v1.3.0  –  Sovereign Command Hub  🔱

  ✔  5 modules loaded and fused.

  #   Module           Description
  1   config-manager   View and edit the hub's JSON configuration file
  2   logger           View the OMEGA application log and configure log verbosity
  3   scheduler        Create, list and control periodic background tasks
  4   system-info      Display live system resource statistics (CPU / RAM / disk / network)
  5   task-runner      Execute shell commands and capture / display their output
```

---

## Requirements

- Python ≥ 3.10
- See `requirements.txt` for third-party dependencies

```
pip install -r requirements.txt
```

---

## Quick start

```bash
python main.py
```

The interactive menu lets you select any module by number, view the execution
audit log (`a`), or quit (`q`).

---

## Architecture

```
omega/
├── __init__.py          # Package metadata / version
├── core.py              # FusionEngine – orchestrator
├── registry.py          # ModuleRegistry – auto-discovers BaseModule subclasses
└── modules/
    ├── base.py          # Abstract BaseModule
    ├── config_manager.py
    ├── logger.py
    ├── scheduler.py
    ├── system_info.py
    └── task_runner.py
main.py                  # CLI entry point
tests/
└── test_omega.py        # Unit tests (pytest)
```

### Adding a new module

1. Create `omega/modules/my_module.py`.
2. Define a class that extends `BaseModule`, sets `name` and `description`, and
   implements `run()`.
3. The `ModuleRegistry` will discover it automatically on next launch — no
   registration step required.

---

## Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## License

See [LICENSE](LICENSE).
