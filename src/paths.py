from pathlib import Path


def get_project_root():
    return Path(__file__).resolve().parent.parent