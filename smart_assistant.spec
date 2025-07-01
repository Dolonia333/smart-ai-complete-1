# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analyze all Python files and their dependencies
a = Analysis(
    ['gui_app.py'],
    pathex=['C:\\Users\\zionv\\OneDrive\\Desktop\\Smart Local Assistant'],
    binaries=[],
    datas=[
        ('plugins', 'plugins'),
        ('config.json', '.'),
        ('knowledge_base.json', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'json',
        'datetime',
        'threading',
        'queue',
        'subprocess',
        'importlib',
        'importlib.util',
        'requests',
        'urllib.parse',
        'webbrowser',
        'os',
        'sys',
        'platform',
        'speech_recognition',
        'pyttsx3',
        'pyaudio',
        'win32gui',
        'win32con',
        'win32api',
        'psutil',
        'pyautogui',
        'BeautifulSoup4',
        'bs4',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SmartAIAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Add icon if available
    version_file=None,
)
