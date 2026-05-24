# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Vox.
# Run via: pyinstaller vox.spec  (from any ASCII-only build directory)

import os
import importlib.util

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


def _vosk_dlls():
    """Locate Vosk's bundled DLLs in the installed package."""
    spec = importlib.util.find_spec('vosk')
    if not spec or not spec.origin:
        return []
    vosk_dir = os.path.dirname(spec.origin)
    dlls = ['libvosk.dll', 'libgcc_s_seh-1.dll',
            'libstdc++-6.dll', 'libwinpthread-1.dll']
    return [(os.path.join(vosk_dir, d), 'vosk')
            for d in dlls if os.path.exists(os.path.join(vosk_dir, d))]


# sherpa-onnx ships native .dll files alongside its Python bindings.
# `collect_dynamic_libs` finds them; `collect_data_files` picks up any
# non-Python assets (e.g., type stubs) so PyInstaller doesn't drop them.
_sherpa_binaries = collect_dynamic_libs('sherpa_onnx')
_sherpa_datas = collect_data_files('sherpa_onnx')


a = Analysis(
    ['vox.py'],
    pathex=[],
    binaries=_vosk_dlls() + _sherpa_binaries,
    datas=[('vox.ico', '.')] + _sherpa_datas,
    hiddenimports=[
        'sherpa_onnx',
        'voxapp', 'voxapp.config', 'voxapp.terms', 'voxapp.punctuation',
        'voxapp.registry', 'voxapp.downloader', 'voxapp.engines',
        'voxapp.worker', 'voxapp.tray', 'voxapp.gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'pandas', 'scipy', 'matplotlib', 'cv2', 'tensorflow',
        'sklearn', 'pytest', 'IPython', 'jupyter', 'pygments', 'boto3',
        'pyarrow', 'cryptography', 'sqlalchemy', 'django', 'flask',
        'fastapi', 'pydantic', 'yt_dlp', 'mutagen', 'curl_cffi',
        'websockets', 'psutil', 'playwright',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='vox',
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
    icon=['vox.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='vox',
)
