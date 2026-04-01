from __future__ import annotations

import os
import sys
from pathlib import Path

_DLL_HANDLES: list[object] = []


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _venv_site_packages() -> Path:
    return _project_root() / ".venv" / "Lib" / "site-packages"


def bootstrap_local_dependencies() -> None:
    """Allow `py .\\main.py` to use the project's local virtualenv packages."""
    site_packages = _venv_site_packages()
    if not site_packages.exists():
        return

    site_packages_text = str(site_packages)
    if site_packages_text not in sys.path:
        sys.path.insert(0, site_packages_text)

    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    candidate_dirs = [
        site_packages / "PySide6",
        site_packages / "shiboken6",
        site_packages / "numpy.libs",
        _project_root() / ".venv" / "Scripts",
    ]
    for dll_dir in candidate_dirs:
        if dll_dir.exists():
            _DLL_HANDLES.append(os.add_dll_directory(str(dll_dir)))
