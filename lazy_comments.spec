# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Lazy Comments.

import os
import importlib.util

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules


def _vosk_dlls():
    spec = importlib.util.find_spec('vosk')
    if not spec or not spec.origin:
        return []
    vosk_dir = os.path.dirname(spec.origin)
    dlls = ['libvosk.dll', 'libgcc_s_seh-1.dll',
            'libstdc++-6.dll', 'libwinpthread-1.dll']
    return [(os.path.join(vosk_dir, d), 'vosk')
            for d in dlls if os.path.exists(os.path.join(vosk_dir, d))]


_sherpa_binaries = collect_dynamic_libs('sherpa_onnx')
_sherpa_datas = collect_data_files('sherpa_onnx')


a = Analysis(
    ['lazy_comments.py'],
    pathex=['.'],
    binaries=_vosk_dlls() + _sherpa_binaries,
    datas=[
        ('lazy_comments.ico', '.'),
        ('lazy_comments/__init__.py', 'lazy_comments'),
    ] + _sherpa_datas,
    hiddenimports=[
        'sherpa_onnx',
        *collect_submodules('lazy_comments'),
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
    name='lazy_comments',
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
    icon=['lazy_comments.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lazy_comments',
)
