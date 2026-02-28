import sys
from setuptools import setup

# Increase recursion depth for complex dependency scanning in Python 3.12
sys.setrecursionlimit(5000)

APP = ['main.py']
DATA_FILES = [
    'assets',
    'soul.md',       # 會在首次啟動時複製到 Library/Application Support 避免打包後唯讀
    'config.json',   # 會在首次啟動時複製到 Library/Application Support 避免打包後唯讀
    # 'memory',        # 不打包對話記憶
    # 'vocab',         # 不打包個人詞庫
    # 'stats'          # 不打包統計資料
]

# Refined options to avoid RecursionError in modulegraph
# Using includes instead of packages for core libs can sometimes help
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icon.icns',
    'plist': {
        'LSUIElement': False, # 暫時顯示 Dock 圖示以確保 TCC 權限攔截順利
        'CFBundleName': "VoiceType4TW-Mac",
        'CFBundleDisplayName': "VoiceType4TW-Mac",
        'CFBundleIdentifier': "com.jimmy4tw.voicetype4tw-mac",
        'NSPrincipalClass': 'NSApplication',
        'CFBundleVersion': "2.2.2",
        'CFBundleShortVersionString': "2.2.2",
        'NSMicrophoneUsageDescription': "VoiceType needs microphone access to transcribe your speech.",
        'NSAccessibilityUsageDescription': "VoiceType needs accessibility access to listen for global hotkeys and inject text.",
        'NSAppleEventsUsageDescription': "VoiceType needs to send events to other apps for text injection.",
        'NSSupportsAutomaticGraphicsSwitching': True,
        'NSHighResolutionCapable': True,
    },
    'packages': ['rumps', 'PyQt6', 'faster_whisper', 'pynput', 'pyperclip', 'sounddevice', '_sounddevice_data', 'httpx', 'certifi', 'objc', 'Quartz'],
    'includes': ['numpy'],
    'excludes': ['tkinter', 'unittest'],
}

setup(
    app=APP,
    name="VoiceType4TW-Mac",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
