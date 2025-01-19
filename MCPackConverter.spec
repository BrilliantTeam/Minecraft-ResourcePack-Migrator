# -*- mode: python ; coding: utf-8 -*-

# Define the analysis configuration for PyInstaller
a = Analysis(
    ['gui_app.py'],            # Main script to build
    pathex=[],                 # Additional paths to search for imports
    binaries=[],              # Additional binary files to include
    datas=[                   # Additional data files to include
        ('converter.py', '.'),
        ('run.py', '.'),
        ('assets/icon.ico', 'assets')
    ],
    hiddenimports=[          # Additional imports that PyInstaller might miss
        'tkinter',
        'rich',
        'rich.console',
        'rich.table',
        'rich.panel',
        'rich.progress',
        'rich.style',
        'threading',
        'json',
        'datetime',
        'pathlib',
        'shutil',
        'zipfile',
        'tempfile',
        'errno',
        'stat'
    ],
    hookspath=[],            # Additional hooks path
    hooksconfig={},          # Hooks configuration
    runtime_hooks=[],        # Runtime hooks
    excludes=[],            # Modules to exclude
    noarchive=False,        # Whether to use archive
)

# Create the Python executable ZIP archive
pyz = PYZ(a.pure)

# Define the executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MCPackConverter',              # Output executable name
    debug=False,                         # Debug mode flag
    bootloader_ignore_signals=False,     # Bootloader signal handling
    strip=False,                         # Strip debug symbols
    upx=True,                           # Use UPX compression
    upx_exclude=[],                     # Files to exclude from UPX compression
    runtime_tmpdir=None,                # Runtime temporary directory
    console=False,                      # GUI mode (no console window)
    disable_windowed_traceback=False,   # Enable traceback in windowed mode
    argv_emulation=False,               # Command line argument emulation
    target_arch=None,                   # Target architecture
    codesign_identity=None,             # Code signing identity
    entitlements_file=None,             # Entitlements file
    manifest='uac_manifest.xml',        # Use the UAC manifest file
    icon='assets\icon.ico'             # EXE Icon
)