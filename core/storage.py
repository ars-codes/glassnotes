"""File save/load logic for FloatNote v2 multi-file notes and window config."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path.home() / "Documents" / "FloatNote"
NOTES_ROOT = NOTES_DIR / "notes"
NOTES_FILE_V1 = NOTES_DIR / "notes.txt"
CONFIG_FILE = NOTES_DIR / "config.json"
BACKUPS_DIR = NOTES_DIR / "backups"
MAX_BACKUPS = 10
DEFAULT_CATEGORY = "General"
DEFAULT_NOTE_NAME = "Quick Notes.md"

DEFAULT_CONFIG: dict = {
    "window": {
        "x": 100,
        "y": 100,
        "height": 320,
        "collapsed": False,
    },
    "visible": True,
    "active_category": DEFAULT_CATEGORY,
    "active_note": DEFAULT_NOTE_NAME,
    "preview_mode": False,
}

WELCOME_CONTENT = """# Welcome to FloatNote v2 ✨

FloatNote is your lightweight, always-on-top desktop scratchpad.

### What's new in v2:
- **Multi-File & Folders:** Click the menu (≡) in the header to create and organize notes in folders.
- **Markdown Preview:** Click the 👁 icon in the header (or press `Ctrl+P`) to toggle rendered view.
- **Smart Anchoring:** Dock on either screen edge—expanding now smartly keeps your window in view!

### Formatting Quick Reference:
- **Bold text** and *italic text*
- [x] Checklists for quick tasks
- `Inline code` and code blocks
- > Quotes and inspirations

*Auto-saves continuously as you type.*
"""


def sanitize_name(name: str) -> str:
    """Strip illegal filesystem characters from names."""
    sanitized = re.sub(r'[<>:"/\\|?*]', "", name).strip()
    sanitized = sanitized.strip(". ")
    return sanitized


def ensure_dirs() -> None:
    """Create FloatNote data directories and perform v1 migration if needed."""
    try:
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        NOTES_ROOT.mkdir(parents=True, exist_ok=True)
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        (NOTES_ROOT / DEFAULT_CATEGORY).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    _migrate_v1_notes_if_present()
    _ensure_at_least_one_note()


def _migrate_v1_notes_if_present() -> None:
    """Migrate legacy v1 notes.txt to General/notes.txt if found."""
    try:
        if NOTES_FILE_V1.is_file():
            content = NOTES_FILE_V1.read_text(encoding="utf-8")
            dest = NOTES_ROOT / DEFAULT_CATEGORY / "notes.txt"
            if not dest.is_file() and content.strip():
                dest.write_text(content, encoding="utf-8")
            # Preserve the old file as a backup archive so migration does not repeat
            bak_path = NOTES_DIR / "notes.txt.v1.bak"
            if not bak_path.is_file():
                shutil.copy2(NOTES_FILE_V1, bak_path)
            try:
                NOTES_FILE_V1.unlink()
            except OSError:
                pass
    except OSError:
        pass


def _get_category_dirs() -> list[str]:
    """Return raw list of directory names under NOTES_ROOT without triggering recursion."""
    categories = []
    try:
        if NOTES_ROOT.is_dir():
            for entry in NOTES_ROOT.iterdir():
                if entry.is_dir() and not entry.name.startswith("."):
                    categories.append(entry.name)
    except OSError:
        pass
    return categories


def _ensure_at_least_one_note() -> None:
    """Ensure that the user has at least one note available upon launch."""
    try:
        categories = _get_category_dirs()
        has_any_file = False
        for cat in categories:
            if list_notes_in_category(cat):
                has_any_file = True
                break
        if not has_any_file:
            starter = NOTES_ROOT / DEFAULT_CATEGORY / DEFAULT_NOTE_NAME
            starter.parent.mkdir(parents=True, exist_ok=True)
            starter.write_text(WELCOME_CONTENT, encoding="utf-8")
    except OSError:
        pass


def list_categories() -> list[str]:
    """Return sorted list of category folder names under NOTES_ROOT."""
    ensure_dirs()
    categories = _get_category_dirs()
    if DEFAULT_CATEGORY not in categories:
        categories.insert(0, DEFAULT_CATEGORY)
    else:
        # Keep DEFAULT_CATEGORY at the top, others alphabetical
        categories.sort(key=lambda c: (c != DEFAULT_CATEGORY, c.lower()))
    return categories


def create_category(category: str) -> bool:
    """Create a new category folder under NOTES_ROOT."""
    if not category or not category.strip():
        return False
    clean = sanitize_name(category)
    if not clean:
        return False
    target = NOTES_ROOT / clean
    try:
        target.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def list_notes_in_category(category: str) -> list[str]:
    """Return sorted list of filenames in a category."""
    cat_dir = NOTES_ROOT / category
    if not cat_dir.is_dir():
        return []
    notes = []
    try:
        for entry in cat_dir.iterdir():
            if entry.is_file() and not entry.name.startswith("."):
                notes.append(entry.name)
    except OSError:
        pass
    notes.sort(key=lambda s: s.lower())
    return notes


def get_category_path(category: str) -> Path:
    """Return full Path to a category folder."""
    return NOTES_ROOT / category


def get_note_path(category: str, filename: str) -> Path:
    """Return full Path to a note file."""
    return NOTES_ROOT / category / filename


def load_note(category: str, filename: str) -> str:
    """Read and return content of a note."""
    ensure_dirs()
    path = get_note_path(category, filename)
    try:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        pass
    return ""


def save_note(category: str, filename: str, content: str) -> None:
    """Atomically write note content."""
    ensure_dirs()
    cat_dir = NOTES_ROOT / category
    try:
        cat_dir.mkdir(parents=True, exist_ok=True)
        dest = cat_dir / filename
        fd, tmp_path = tempfile.mkstemp(
            dir=str(cat_dir), suffix=".tmp", prefix="note_"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
            os.replace(tmp_path, dest)
        except OSError:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except OSError:
        pass


def create_note(category: str, filename: str, content: str = "") -> Path | None:
    """Create a new note file with given filename and optional content."""
    ensure_dirs()
    clean_cat = sanitize_name(category) or DEFAULT_CATEGORY
    clean_name = sanitize_name(filename)
    if not clean_name:
        return None

    # Default to .md if no extension provided
    if not (clean_name.endswith(".md") or clean_name.endswith(".txt")):
        clean_name += ".md"

    cat_dir = NOTES_ROOT / clean_cat
    cat_dir.mkdir(parents=True, exist_ok=True)
    dest = cat_dir / clean_name
    try:
        if not dest.is_file():
            dest.write_text(content, encoding="utf-8")
        return dest
    except OSError:
        return None


def delete_note(category: str, filename: str) -> bool:
    """Delete a note file."""
    path = get_note_path(category, filename)
    try:
        if path.is_file():
            path.unlink()
            return True
    except OSError:
        pass
    return False


def rename_note(category: str, old_filename: str, new_filename: str) -> bool:
    """Rename a note file within the same category."""
    clean_new = sanitize_name(new_filename)
    if not clean_new:
        return False
    # Preserve extension if user did not specify one
    old_ext = Path(old_filename).suffix
    if not Path(clean_new).suffix and old_ext:
        clean_new += old_ext

    src = get_note_path(category, old_filename)
    dst = get_note_path(category, clean_new)
    if not src.is_file() or (dst.is_file() and src != dst):
        return False
    try:
        src.rename(dst)
        return True
    except OSError:
        return False


def move_note(old_category: str, filename: str, new_category: str) -> bool:
    """Move a note file to another category."""
    clean_cat = sanitize_name(new_category) or DEFAULT_CATEGORY
    src = get_note_path(old_category, filename)
    dst_dir = NOTES_ROOT / clean_cat
    dst = dst_dir / filename
    if not src.is_file() or dst.is_file():
        return False
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return True
    except OSError:
        return False


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


def resolve_active_note(config: dict) -> tuple[str, str]:
    """Return valid (category, filename) based on config or existing notes."""
    ensure_dirs()
    cat = config.get("active_category", DEFAULT_CATEGORY)
    note = config.get("active_note", DEFAULT_NOTE_NAME)

    if get_note_path(cat, note).is_file():
        return cat, note

    # Check other notes in active category
    notes = list_notes_in_category(cat)
    if notes:
        return cat, notes[0]

    # Check any notes in any category
    categories = list_categories()
    for c in categories:
        c_notes = list_notes_in_category(c)
        if c_notes:
            return c, c_notes[0]

    # If all empty, create default starter note
    create_note(DEFAULT_CATEGORY, DEFAULT_NOTE_NAME, WELCOME_CONTENT)
    return DEFAULT_CATEGORY, DEFAULT_NOTE_NAME


def create_backup(category: str | None = None, filename: str | None = None) -> None:
    """Write a timestamped backup of the specified note or active notes."""
    ensure_dirs()
    try:
        if not category or not filename:
            cfg = load_config()
            category, filename = resolve_active_note(cfg)

        path = get_note_path(category, filename)
        if not path.is_file():
            return

        text = path.read_text(encoding="utf-8")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_base = sanitize_name(f"{category}_{filename}")
        backup_path = BACKUPS_DIR / f"{safe_base}_{stamp}.bak"
        backup_path.write_text(text, encoding="utf-8")
        _prune_backups()
    except OSError:
        pass


def _prune_backups() -> None:
    """Keep only the newest MAX_BACKUPS backup files."""
    try:
        backups = sorted(
            BACKUPS_DIR.glob("*.bak"),
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

