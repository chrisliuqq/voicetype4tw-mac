import sys
from setuptools import setup

# Increase recursion depth for complex dependency scanning in Python 3.12
sys.setrecursionlimit(5000)

APP = ['main.py']
DATA_FILES = [
    'assets',
    # 'soul.md',       # 不打包個人化提示詞，保護隱私
    # 'config.json',   # 不打包 API Key，避免洩漏
    # 'memory',        # 不打包對話記憶
    # 'vocab',         # 不打包個人詞庫
    # 'stats'          # 不打包統計資料
]

# Refined options to avoid RecursionError in modulegraph
# Using includes instead of packages for core libs can sometimes help
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/icon.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': "VoiceType4TW-Mac",
        'CFBundleDisplayName': "VoiceType4TW-Mac",
        'CFBundleIdentifier': "com.jimmychu.voicetype4tw-mac",
        'CFBundleVersion': "2.2.0",
        'CFBundleShortVersionString': "2.2.0",
        'NSMicrophoneUsageDescription': "VoiceType needs microphone access to transcribe your speech.",
    },
    'packages': ['rumps', 'PyQt6', 'faster_whisper', 'pynput', 'pyperclip', 'sounddevice', '_sounddevice_data', 'httpx', 'certifi'],
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
