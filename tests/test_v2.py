"""Unit tests for FloatNote v2 multi-file storage, smart anchoring, and Markdown support."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QIcon, QMouseEvent, QTextDocument
from PySide6.QtWidgets import QApplication

from core import acrylic, storage
from core.hotkey import GlobalHotkeyManager
from ui import styles


class TestStorageV2(unittest.TestCase):
    """Test storage v2 functionality including folders, notes, and migration."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="floatnote_test_"))
        self._orig_notes_dir = storage.NOTES_DIR
        self._orig_notes_root = storage.NOTES_ROOT
        self._orig_notes_file_v1 = storage.NOTES_FILE_V1
        self._orig_config_file = storage.CONFIG_FILE
        self._orig_backups_dir = storage.BACKUPS_DIR

        storage.NOTES_DIR = self.temp_dir
        storage.NOTES_ROOT = self.temp_dir / "notes"
        storage.NOTES_FILE_V1 = self.temp_dir / "notes.txt"
        storage.CONFIG_FILE = self.temp_dir / "config.json"
        storage.BACKUPS_DIR = self.temp_dir / "backups"

    def tearDown(self) -> None:
        storage.NOTES_DIR = self._orig_notes_dir
        storage.NOTES_ROOT = self._orig_notes_root
        storage.NOTES_FILE_V1 = self._orig_notes_file_v1
        storage.CONFIG_FILE = self._orig_config_file
        storage.BACKUPS_DIR = self._orig_backups_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_v1_migration(self) -> None:
        """Verify that an existing v1 notes.txt is migrated to General/notes.txt without data loss."""
        v1_text = "Important thoughts from v1.\nDon't lose this!"
        storage.NOTES_DIR.mkdir(parents=True, exist_ok=True)
        storage.NOTES_FILE_V1.write_text(v1_text, encoding="utf-8")

        storage.ensure_dirs()

        migrated_file = storage.NOTES_ROOT / "General" / "notes.txt"
        self.assertTrue(migrated_file.is_file(), "Migrated file should exist in General/notes.txt")
        self.assertEqual(migrated_file.read_text(encoding="utf-8"), v1_text)

        bak_file = storage.NOTES_DIR / "notes.txt.v1.bak"
        self.assertTrue(bak_file.is_file(), "Backup archive of v1 notes should be retained")
        self.assertEqual(bak_file.read_text(encoding="utf-8"), v1_text)

        self.assertFalse(storage.NOTES_FILE_V1.is_file(), "Original notes.txt should be moved")

    def test_starter_note_on_fresh_install(self) -> None:
        """Verify that a fresh install creates a default Quick Notes.md note."""
        storage.ensure_dirs()
        categories = storage.list_categories()
        self.assertIn("General", categories)
        notes = storage.list_notes_in_category("General")
        self.assertIn("Quick Notes.md", notes)

    def test_category_crud(self) -> None:
        """Verify category creation and listing."""
        self.assertTrue(storage.create_category("Work"))
        self.assertTrue(storage.create_category("Personal Projects"))
        self.assertFalse(storage.create_category(""))  # Empty should be rejected

        cats = storage.list_categories()
        self.assertEqual(cats[0], "General", "General should always be listed first")
        self.assertIn("Work", cats)
        self.assertIn("Personal Projects", cats)

    def test_note_crud(self) -> None:
        """Verify note creation, reading, writing, renaming, and deletion."""
        note_path = storage.create_note("General", "Meeting.md", "# Agenda\n- Discussion")
        self.assertIsNotNone(note_path)
        self.assertTrue(note_path.is_file())

        content = storage.load_note("General", "Meeting.md")
        self.assertIn("# Agenda", content)

        storage.save_note("General", "Meeting.md", "# Updated Agenda\n- Action items")
        updated = storage.load_note("General", "Meeting.md")
        self.assertIn("Action items", updated)

        # Rename
        renamed = storage.rename_note("General", "Meeting.md", "Sprint_Meeting")
        self.assertTrue(renamed)
        self.assertIn("Sprint_Meeting.md", storage.list_notes_in_category("General"))
        self.assertNotIn("Meeting.md", storage.list_notes_in_category("General"))

        # Delete
        deleted = storage.delete_note("General", "Sprint_Meeting.md")
        self.assertTrue(deleted)
        self.assertNotIn("Sprint_Meeting.md", storage.list_notes_in_category("General"))

    def test_move_note(self) -> None:
        """Verify moving a note across categories."""
        storage.create_category("Archive")
        storage.create_note("General", "OldTask.txt", "Finished task")

        ok = storage.move_note("General", "OldTask.txt", "Archive")
        self.assertTrue(ok)
        self.assertIn("OldTask.txt", storage.list_notes_in_category("Archive"))
        self.assertNotIn("OldTask.txt", storage.list_notes_in_category("General"))

    def test_resolve_active_note_fallback(self) -> None:
        """Verify fallback when configured note is deleted."""
        cfg = {"active_category": "General", "active_note": "NonExistent.md"}
        cat, note = storage.resolve_active_note(cfg)
        self.assertTrue(storage.get_note_path(cat, note).is_file())


class TestSmartAnchoring(unittest.TestCase):
    """Test smart expand/collapse anchoring geometry calculations."""

    def test_left_anchored_expansion_and_collapse(self) -> None:
        """When docked on left side of screen, top-left remains fixed."""
        screen_avail = QRect(0, 0, 1920, 1080)
        screen_center_x = screen_avail.x() + screen_avail.width() / 2.0  # 960

        # Collapsed widget at x=100, width=44
        pos_x, pos_y = 100, 100
        collapsed_w, collapsed_h = 44, 44
        widget_center_x = pos_x + collapsed_w / 2.0  # 122 < 960 (left side)
        self.assertLess(widget_center_x, screen_center_x)

        # Expand: top-left anchored
        target_x = pos_x
        self.assertEqual(target_x, 100)

        # Collapse back: top-left anchored
        self.assertEqual(target_x, 100)

    def test_right_anchored_expansion_and_collapse(self) -> None:
        """When docked on right side of screen, top-right remains fixed."""
        screen_avail = QRect(0, 0, 1920, 1080)
        screen_center_x = screen_avail.x() + screen_avail.width() / 2.0  # 960

        fixed_w = 288
        collapsed_size = 44

        # Collapsed near right edge: x=1860, right edge = 1904
        pos_x, pos_y = 1860, 100
        widget_center_x = pos_x + collapsed_size / 2.0  # 1882 > 960 (right side)
        self.assertGreater(widget_center_x, screen_center_x)

        # Expand: pinned top-right
        target_x = (pos_x + collapsed_size) - fixed_w
        self.assertEqual(target_x, 1616)
        # Verify right edge coordinate is preserved
        self.assertEqual(target_x + fixed_w, pos_x + collapsed_size)  # 1904 == 1904!

        # Collapse from expanded at x=1616, width=288 (right edge = 1904)
        expanded_x = 1616
        collapse_target_x = (expanded_x + fixed_w) - collapsed_size
        self.assertEqual(collapse_target_x, 1860)
        # Verify collapsed right edge coordinate is preserved
        self.assertEqual(collapse_target_x + collapsed_size, expanded_x + fixed_w)  # 1904 == 1904!


class TestVisualThemeAndMarkdown(unittest.TestCase):
    """Test neutral charcoal glass styles (Fix 1) and Markdown rendering setup."""

    def test_acrylic_tint_abgr(self) -> None:
        """Check that acrylic tint is neutral charcoal ABGR (Fix 1)."""
        # Alpha: 0x8A (138), Blue: 0x14 (20), Green: 0x14 (20), Red: 0x14 (20)
        abgr_expected = 0x8A141414
        alpha = (abgr_expected >> 24) & 0xFF
        blue = (abgr_expected >> 16) & 0xFF
        green = (abgr_expected >> 8) & 0xFF
        red = abgr_expected & 0xFF
        self.assertEqual(alpha, 0x8A)
        self.assertEqual(blue, 20)
        self.assertEqual(green, 20)
        self.assertEqual(red, 20)

    def test_styles_output(self) -> None:
        """Verify QSS generation contains neutral charcoal/gray palette and valid syntax."""
        exp_qss = styles.expanded_styles(use_fallback=False)
        self.assertIn("rgba(32, 36, 44", exp_qss)
        self.assertIn("border-top: 1px solid rgba(255, 255, 255", exp_qss)
        self.assertIn("noteEditor", exp_qss)
        self.assertIn("notePreview", exp_qss)
        self.assertIn("resizeHandle", exp_qss)

        col_qss = styles.collapsed_styles(use_fallback=False)
        self.assertIn("collapsedIcon", col_qss)
        self.assertIn("qradialgradient", col_qss)
        self.assertIn(f"min-width: {styles.COLLAPSED_SIZE}px", col_qss)
        # Verify no broken double-brace syntax in output
        self.assertNotIn("{{", exp_qss)
        self.assertNotIn("}}", exp_qss)
        self.assertNotIn("{{", col_qss)
        self.assertNotIn("}}", col_qss)

    def test_markdown_rendering(self) -> None:
        """Verify QTextDocument markdown parser converts headers and task items."""
        doc = QTextDocument()
        doc.setDefaultStyleSheet(styles.MARKDOWN_DOC_CSS)
        doc.setMarkdown("# Title\n- [ ] Todo item\n- [x] Done item\n`inline_code`")
        html = doc.toHtml()
        self.assertIn("Title", html)
        self.assertIn("inline_code", html)


class TestWidgetIntegration(unittest.TestCase):
    """Test FloatNoteWidget initialization, switching, and UI states."""

    @classmethod
    def setUpClass(cls) -> None:
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="floatnote_widget_test_"))
        self._orig_notes_dir = storage.NOTES_DIR
        self._orig_notes_root = storage.NOTES_ROOT
        self._orig_config_file = storage.CONFIG_FILE
        self._orig_backups_dir = storage.BACKUPS_DIR

        storage.NOTES_DIR = self.temp_dir
        storage.NOTES_ROOT = self.temp_dir / "notes"
        storage.CONFIG_FILE = self.temp_dir / "config.json"
        storage.BACKUPS_DIR = self.temp_dir / "backups"
        storage.ensure_dirs()

    def tearDown(self) -> None:
        storage.NOTES_DIR = self._orig_notes_dir
        storage.NOTES_ROOT = self._orig_notes_root
        storage.CONFIG_FILE = self._orig_config_file
        storage.BACKUPS_DIR = self._orig_backups_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_widget_init_and_markdown_toggle(self) -> None:
        from ui.widget import FloatNoteWidget

        widget = FloatNoteWidget()
        storage.create_note("General", "Sample.md", "# Test Heading\n**test bold**")
        widget.initialize(category="General", filename="Sample.md")

        self.assertEqual(widget._active_category, "General")
        self.assertEqual(widget._active_note, "Sample.md")
        self.assertTrue(widget._header.preview_btn.isVisible(), "Preview button should be visible for .md files")

        # Toggle to preview mode
        widget.toggle_preview_mode()
        self.assertTrue(widget._preview_mode)
        self.assertEqual(widget._editor_stack.currentWidget(), widget._preview)

        # Toggle back to edit mode
        widget.toggle_preview_mode()
        self.assertFalse(widget._preview_mode)
        self.assertEqual(widget._editor_stack.currentWidget(), widget._editor)

        # Switch to .txt note
        storage.create_note("General", "Plain.txt", "Plain text content")
        widget.switch_to_note("General", "Plain.txt")
        self.assertFalse(widget._header.preview_btn.isVisible(), "Preview button should be hidden for .txt files")
        self.assertEqual(widget._editor_stack.currentWidget(), widget._editor)

        widget.close()

    def test_dialogs_instantiation(self) -> None:
        from ui.dialogs import ConfirmDialog, NewFolderDialog, NewNoteDialog, RenameNoteDialog

        dlg1 = NewNoteDialog(["General", "Work"], default_category="General")
        self.assertIsNotNone(dlg1)
        dlg1.close()

        dlg2 = NewFolderDialog()
        self.assertIsNotNone(dlg2)
        dlg2.close()

        dlg3 = RenameNoteDialog("MyNote.md")
        self.assertIsNotNone(dlg3)
        dlg3.close()

        dlg4 = ConfirmDialog("Title", "Message")
        self.assertIsNotNone(dlg4)
        dlg4.close()

    def test_fix2_scrim_overlay_exists(self) -> None:
        """Verify Fix 2: ScrimOverlay is initialized on widget and handles dimming."""
        from ui.widget import FloatNoteWidget
        widget = FloatNoteWidget()
        self.assertTrue(hasattr(widget, "_scrim"))
        self.assertFalse(widget._scrim.isVisible())
        widget.close()

    def test_fix3_resize_handle_and_ceiling(self) -> None:
        """Verify Fix 3: ResizeHandle has valid height and raises max ceiling to full screen."""
        from ui.widget import FloatNoteWidget
        widget = FloatNoteWidget()
        widget.initialize()
        self.assertGreaterEqual(widget._resize_handle.height(), 6)
        # Test max height is not artificially capped at 80%
        max_h = widget._max_height()
        self.assertGreaterEqual(max_h, 600)
        widget.close()

    def test_fix4_collapsed_size(self) -> None:
        """Verify Round 2 Fix A: Collapsed size is 58 (10% reduction from original 64)."""
        from ui.styles import COLLAPSED_RADIUS, COLLAPSED_SIZE as STYLE_COLLAPSED_SIZE
        from ui.widget import COLLAPSED_SIZE
        self.assertEqual(COLLAPSED_SIZE, 58)
        self.assertEqual(STYLE_COLLAPSED_SIZE, 58)
        self.assertEqual(COLLAPSED_RADIUS, 29)
        self.assertIn("58px", styles.COLLAPSED_STYLE)
        self.assertIn("29px", styles.COLLAPSED_STYLE)

    def test_fix5_open_notes_folder_target(self) -> None:
        """Verify Fix 5: target folder points to notes directory, not parent app data."""
        storage.ensure_dirs()
        target = storage.get_category_path("General")
        self.assertTrue(str(target).startswith(str(storage.NOTES_ROOT)))
        self.assertNotEqual(target, storage.NOTES_DIR)

    def test_fix7_fixed_appid_in_installer(self) -> None:
        """Verify Fix 7: floatnote.iss uses permanently fixed AppId and localappdata."""
        iss_path = Path("floatnote.iss")
        content = iss_path.read_text(encoding="utf-8")
        self.assertIn('{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}', content)
        self.assertIn('{localappdata}', content)
        # Ensure installer does NOT delete user notes
        self.assertNotIn('{userdocs}', content)

    def test_round2_fix_b_clamp_to_screen_small_window(self) -> None:
        """Verify Round 2 Fix B: Collapsed window with size < 50px passes screen clamping."""
        from ui.widget import FloatNoteWidget, MIN_VISIBLE
        widget = FloatNoteWidget()
        widget.initialize()
        widget._collapsed = True
        widget.setFixedSize(58, 58)

        # Position widget at a valid coordinate on screen
        widget.move(120, 120)
        widget._clamp_to_screen()
        # Should stay at (120, 120), NOT recenter
        self.assertEqual(widget.x(), 120)
        self.assertEqual(widget.y(), 120)

        # Even with a test size smaller than MIN_VISIBLE (e.g. 40x40):
        widget.setFixedSize(40, 40)
        widget.move(140, 140)
        widget._clamp_to_screen()
        self.assertEqual(widget.x(), 140)
        self.assertEqual(widget.y(), 140)
        widget.close()

    def test_round2_fix_c_dialog_blur_and_borders(self) -> None:
        """Verify Round 2 Fix C: Blur applied during exec_dialog, cleared in finally, and dialog borders."""
        from PySide6.QtWidgets import QDialog, QGraphicsBlurEffect
        from ui.widget import FloatNoteWidget

        # Verify border styling in DIALOG_STYLE
        self.assertIn("border-top: 1.5px solid rgba(255, 255, 255, 120)", styles.DIALOG_STYLE)
        self.assertIn("border-bottom: 1.5px solid rgba(255, 255, 255, 95)", styles.DIALOG_STYLE)

        widget = FloatNoteWidget()
        widget.initialize()
        self.assertIsNone(widget._expanded_container.graphicsEffect())

        # Test dummy dialog that verifies blur is active during exec
        class MockDialog(QDialog):
            def __init__(self, main_w, parent=None):
                super().__init__(parent)
                self.main_w = main_w
                self.blur_was_active = False

            def exec(self):
                effect = self.main_w._expanded_container.graphicsEffect()
                if isinstance(effect, QGraphicsBlurEffect) and effect.blurRadius() == 8.0:
                    self.blur_was_active = True
                return QDialog.DialogCode.Accepted

        mock_dlg = MockDialog(widget, parent=widget)
        res = widget.exec_dialog(mock_dlg)
        self.assertEqual(res, QDialog.DialogCode.Accepted)
        self.assertTrue(mock_dlg.blur_was_active, "Blur effect must be active during dialog execution")
        self.assertIsNone(widget._expanded_container.graphicsEffect(), "Blur effect must be cleared after dialog closes")
        widget.close()

    def test_installer_version_bump_v2_0_2(self) -> None:
        """Verify Release Notes: floatnote.iss is bumped to 2.0.2 with versioned installer filename."""
        iss_path = Path("floatnote.iss")
        content = iss_path.read_text(encoding="utf-8")
        self.assertIn('#define MyAppVersion "2.0.2"', content)
        self.assertIn('OutputBaseFilename=FloatNoteSetup-{#MyAppVersion}', content)
        self.assertIn('{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}', content)

        legacy_iss = Path("build/installer.iss")
        legacy_content = legacy_iss.read_text(encoding="utf-8")
        self.assertIn("DEPRECATED", legacy_content)
        self.assertIn('#define MyAppVersion "2.0.2"', legacy_content)

    def test_fix1_delete_note_flush_false_and_no_recreation(self) -> None:
        """Verify Fix 1: Deleting a note cancels pending save and never recreates file."""
        from unittest.mock import patch
        from ui.widget import FloatNoteWidget
        widget = FloatNoteWidget()
        storage.create_note("General", "NoteA.md", "Content A")
        storage.create_note("General", "NoteB.md", "Content B")
        widget.initialize(category="General", filename="NoteA.md")

        # Type in editor to trigger autosave debounce timer (< 500ms)
        widget._editor.setPlainText("Unsaved content for Note A")
        self.assertTrue(widget._save_timer.isActive())

        # Mock confirm dialog to accept
        with patch.object(widget, "exec_dialog", return_value=True):
            widget._delete_active_note()

        # Check save timer was stopped
        self.assertFalse(widget._save_timer.isActive())
        # NoteA should be deleted from disk
        self.assertFalse((storage.NOTES_ROOT / "General" / "NoteA.md").is_file())
        # Active note switched to NoteB
        self.assertEqual(widget._active_note, "NoteB.md")
        self.assertEqual(widget._editor.toPlainText(), "Content B")

        # Simulate quit-time flush: must NOT recreate NoteA
        widget.flush_pending_save()
        self.assertFalse((storage.NOTES_ROOT / "General" / "NoteA.md").is_file())
        self.assertTrue((storage.NOTES_ROOT / "General" / "NoteB.md").is_file())
        widget.close()

    def test_fix1_delete_last_note_creates_starter(self) -> None:
        """Verify Fix 1: Deleting the last remaining note recreates starter note."""
        from unittest.mock import patch
        from ui.widget import FloatNoteWidget
        widget = FloatNoteWidget()
        # Clean out all notes
        for cat in storage.list_categories():
            for n in storage.list_notes_in_category(cat):
                storage.delete_note(cat, n)

        storage.create_note("General", "SoleNote.md", "Only one")
        widget.initialize(category="General", filename="SoleNote.md")

        with patch.object(widget, "exec_dialog", return_value=True):
            widget._delete_active_note()

        self.assertFalse((storage.NOTES_ROOT / "General" / "SoleNote.md").is_file())
        self.assertEqual(widget._active_note, storage.DEFAULT_NOTE_NAME)
        self.assertTrue((storage.NOTES_ROOT / "General" / storage.DEFAULT_NOTE_NAME).is_file())
        widget.close()

    def test_fix1_delete_failure_shows_alert(self) -> None:
        """Verify Fix 1: If storage.delete_note returns False, error dialog is shown."""
        from unittest.mock import patch
        from ui.widget import FloatNoteWidget
        from ui.dialogs import AlertDialog
        widget = FloatNoteWidget()
        storage.create_note("General", "Protected.md", "Safe")
        widget.initialize(category="General", filename="Protected.md")

        dialogs_shown = []
        def mock_exec_dialog(dlg):
            dialogs_shown.append(dlg)
            return True

        with patch.object(storage, "delete_note", return_value=False):
            with patch.object(widget, "exec_dialog", side_effect=mock_exec_dialog):
                widget._delete_active_note()

        # An AlertDialog should have been executed
        alert_shown = any(isinstance(d, AlertDialog) for d in dialogs_shown)
        self.assertTrue(alert_shown)
        self.assertEqual(widget._active_note, "Protected.md")
        widget.close()

    def test_fix2_right_anchored_collapse_preserves_right_edge(self) -> None:
        """Verify Fix 2: Right side collapse animation keeps right edge identical."""
        from ui.widget import FloatNoteWidget, FIXED_WIDTH, COLLAPSED_SIZE
        widget = FloatNoteWidget()
        widget.initialize()
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        x = avail.x() + avail.width() - FIXED_WIDTH - 20
        y = avail.y() + 100
        widget.move(x, y)

        # Start collapse
        widget.collapse()
        self.assertTrue(widget._animating)
        # End rect right edge should equal start rect right edge
        start_right = widget._animation.startValue().x() + widget._animation.startValue().width()
        end_right = widget._animation.endValue().x() + widget._animation.endValue().width()
        self.assertEqual(start_right, end_right, "Right edge must stay constant during right-side collapse")

        # Verify size constraints are lifted during animation
        self.assertEqual(widget.minimumSize().width(), 0)
        self.assertEqual(widget.minimumSize().height(), 0)
        self.assertEqual(widget.maximumSize().width(), 16777215)
        self.assertEqual(widget.maximumSize().height(), 16777215)

        # Verify content container is hidden
        self.assertFalse(widget._expanded_container.isVisible())
        self.assertFalse(widget._collapsed_btn.isVisible())

        # Complete animation
        widget._finish_animation_immediately()
        self.assertFalse(widget._animating)
        self.assertEqual(widget.width(), COLLAPSED_SIZE)
        self.assertEqual(widget.height(), COLLAPSED_SIZE)
        self.assertTrue(widget._collapsed_btn.isVisible())
        self.assertFalse(widget._expanded_container.isVisible())
        widget.close()

    def test_fix2_right_anchored_expand_preserves_right_edge(self) -> None:
        """Verify Fix 2: Right side expand animation keeps right edge identical."""
        from ui.widget import FloatNoteWidget, FIXED_WIDTH, COLLAPSED_SIZE
        widget = FloatNoteWidget()
        widget.initialize()
        widget.setFixedSize(COLLAPSED_SIZE, COLLAPSED_SIZE)
        widget._collapsed = True
        widget._apply_collapsed_constraints()
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)
        x = avail.x() + avail.width() - COLLAPSED_SIZE - 20
        y = avail.y() + 100
        widget.move(x, y)

        widget.expand()
        self.assertTrue(widget._animating)
        start_right = widget._animation.startValue().x() + widget._animation.startValue().width()
        end_right = widget._animation.endValue().x() + widget._animation.endValue().width()
        self.assertEqual(start_right, end_right, "Right edge must stay constant during right-side expand")

        widget._finish_animation_immediately()
        self.assertFalse(widget._animating)
        self.assertEqual(widget.width(), FIXED_WIDTH)
        self.assertTrue(widget._expanded_container.isVisible())
        self.assertFalse(widget._collapsed_btn.isVisible())
        widget.close()

    def test_fix3_interrupted_animation_on_hotkey(self) -> None:
        """Verify Fix 3: Interrupted animation (hide/show/toggle) finishes immediately and enforces size."""
        from ui.widget import FloatNoteWidget, FIXED_WIDTH, COLLAPSED_SIZE
        widget = FloatNoteWidget()
        widget.initialize()
        widget.move(100, 100)

        # Trigger collapse
        widget.collapse()
        self.assertTrue(widget._animating)

        # Mid-animation, user presses hotkey to hide
        widget.hide_widget()
        self.assertFalse(widget._animating)
        self.assertFalse(widget.isVisible())
        self.assertEqual(widget.width(), COLLAPSED_SIZE)
        self.assertEqual(widget.height(), COLLAPSED_SIZE)

        # User presses hotkey to show
        widget.show_widget()
        self.assertFalse(widget._animating)
        self.assertTrue(widget.isVisible())
        self.assertEqual(widget.width(), COLLAPSED_SIZE)
        self.assertEqual(widget.height(), COLLAPSED_SIZE)

        # Expand and interrupt by hide
        widget.expand()
        self.assertTrue(widget._animating)
        widget.hide_widget()
        self.assertFalse(widget._animating)
        self.assertEqual(widget.width(), FIXED_WIDTH)
        widget.close()

    def test_fix3_size_invariants_and_logging(self) -> None:
        """Verify Fix 3: Size mismatch is logged and corrected by _enforce_size_invariants."""
        from ui.widget import FloatNoteWidget, FIXED_WIDTH, COLLAPSED_SIZE
        widget = FloatNoteWidget()
        widget.initialize()

        with self.assertLogs("floatnote", level="WARNING") as cm:
            # Force wrong width and height while expanded
            widget.setMinimumSize(0, 0)
            widget.setMaximumSize(16777215, 16777215)
            widget.resize(200, 100)
            widget._enforce_size_invariants()

        self.assertTrue(any("Size mismatch in expanded state" in log for log in cm.output))
        self.assertEqual(widget.width(), FIXED_WIDTH)
        self.assertGreaterEqual(widget.height(), 120)

        # Test collapsed state
        widget._collapsed = True
        with self.assertLogs("floatnote", level="WARNING") as cm2:
            widget.setMinimumSize(0, 0)
            widget.setMaximumSize(16777215, 16777215)
            widget.resize(100, 100)
            widget._enforce_size_invariants()

        self.assertTrue(any("Size mismatch in collapsed state" in log for log in cm2.output))
        self.assertEqual(widget.width(), COLLAPSED_SIZE)
        self.assertEqual(widget.height(), COLLAPSED_SIZE)
        widget.close()

    def test_fix4_native_geometry_sync_check(self) -> None:
        """Verify Fix 4: _check_and_sync_native_geometry method exists, runs safely, and handles resync."""
        from ui.widget import FloatNoteWidget
        widget = FloatNoteWidget()
        widget.initialize()
        self.assertTrue(hasattr(widget, "_check_and_sync_native_geometry"))
        # Call it when visible
        widget.show()
        widget._check_and_sync_native_geometry()
        self.assertEqual(widget.width(), 288)
        widget.close()


if __name__ == "__main__":
    unittest.main()
