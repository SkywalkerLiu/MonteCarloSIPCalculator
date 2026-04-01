# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path.cwd()
icon_path = project_root / "assets" / "icons" / "monte_carlo_reserve.ico"

hiddenimports = [
    "matplotlib.backends.backend_qtagg",
]

datas = [
    (str(project_root / "assets"), "assets"),
]


a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MonteCarloSIPCalculator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(icon_path),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="MonteCarloSIPCalculator",
)
