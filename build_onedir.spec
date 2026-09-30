# -*- mode: python ; coding: utf-8 -*-
import os, sys

if sys.platform == 'win32':
    croc_src = os.path.join('croc', 'croc.exe')
    croc_dest = 'croc'
else:
    croc_src = os.path.join('croc', 'croc')
    croc_dest = 'croc'

croc_binaries = [(croc_src, croc_dest)] if os.path.exists(croc_src) else []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=croc_binaries,
    datas=[('lang', 'lang'), ('assets', 'assets'), ('icon.ico', '.'), ('themes.json', '.')],
    hiddenimports=[],
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
    name='SwampSwap',
    icon='icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SwampSwap',
)
