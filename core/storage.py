"""File save/load logic for GlassNotes notes and window config."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path.home() / "Documents" / "GlassNotes"
NOTES_FILE = NOTES_DIR / "notes.txt"
CONFIG_FILE = NOTES_DIR / "config.json"
BACKUPS_DIR = NOTES_DIR / "backups"
MAX_BACKUPS = 10

DEFAULT_CONFIG: dict = {
    "window": {
        "x": 100,
        "y": 100,
        "height": 320,
        "collapsed": False,
    },
    "visible": True,
}


def ensure_dirs() -> None:
    """Create GlassNotes data directories on first run."""
    try:
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


def load_notes() -> str:
    """Load note text; return empty string if missing or unreadable."""
    ensure_dirs()
    try:
        if NOTES_FILE.is_file():
            return NOTES_FILE.read_text(encoding="utf-8")
    except OSError:
        pass
    return ""


def save_notes(text: str) -> None:
    """Overwrite notes.txt with current content."""
    ensure_dirs()
    try:
        NOTES_FILE.write_text(text, encoding="utf-8")
    except OSError:
        pass


def load_config() -> dict:
    """Load window config; return defaults if missing or invalid."""
    ensure_dirs()
    try:
        if CONFIG_FILE.is_file():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                merged = _deep_merge(DEFAULT_CONFIG, data)
                return merged
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(config: dict) -> None:
    """Atomically write config JSON."""
    ensure_dirs()
    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=str(NOTES_DIR), suffix=".tmp", prefix="config_"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(config, handle, indent=2)
            os.replace(tmp_path, CONFIG_FILE)
        except OSError:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except OSError:
        pass


def create_backup() -> None:
    """Write a timestamped backup of notes.txt and prune old backups."""
    ensure_dirs()
    try:
        if not NOTES_FILE.is_file():
            return
        text = NOTES_FILE.read_text(encoding="utf-8")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUPS_DIR / f"notes_{stamp}.txt"
        backup_path.write_text(text, encoding="utf-8")
        _prune_backups()
    except OSError:
        pass


def _prune_backups() -> None:
    """Keep only the newest MAX_BACKUPS backup files."""
    try:
        backups = sorted(
            BACKUPS_DIR.glob("notes_*.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old in backups[MAX_BACKUPS:]:
            try:
                old.unlink()
            except OSError:
                pass
    except OSError:
        pass


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into a copy of base."""
    result = json.loads(json.dumps(base))
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
