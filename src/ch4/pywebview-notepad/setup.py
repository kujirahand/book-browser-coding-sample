from setuptools import setup

APP = ["main.py"]
DATA_FILES = [
    ("static", ["static/index.html", "static/style.css"]),
]
OPTIONS = {
    "argv_emulation": False,
    "packages": ["flask"],
    "plist": {
        "CFBundleName": "PyWebviewNotepad",
        "CFBundleDisplayName": "PyWebviewNotepad",
        "CFBundleIdentifier": "com.example.pywebviewnotepad",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)

