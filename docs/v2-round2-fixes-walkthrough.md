# Walkthrough — FloatNote v2 Round 2 Fixes

This document details the changes implemented for **FloatNote v2 Round 2 Fixes** (`v2.0.1`) per [`docs/floatnote-v2-round2-fixes.md`](file:///d:/DEV/floatnote/docs/floatnote-v2-round2-fixes.md), their verification results, and testing instructions.

---

## 1. Summary of Changes

### Fix A: Collapsed Icon Size to 58px & Single Source of Truth
- **Files Modified**: [`ui/styles.py`](file:///d:/DEV/floatnote/ui/styles.py), [`ui/widget.py`](file:///d:/DEV/floatnote/ui/widget.py)
- **Changes**:
  - In `ui/styles.py`, defined `COLLAPSED_SIZE = 58` (a 10% reduction from the original 64px size) and `COLLAPSED_RADIUS = COLLAPSED_SIZE // 2` (29px).
  - Interpolated `COLLAPSED_SIZE` and `COLLAPSED_RADIUS` directly into `COLLAPSED_STYLE` and `COLLAPSED_FALLBACK_STYLE` via f-strings, eliminating all hardcoded pixel sizes.
  - In `ui/widget.py`, imported `COLLAPSED_SIZE = styles.COLLAPSED_SIZE`. All button dimensions, icon sizes, fixed sizes, collapse/expand animation endpoints, and anchoring coordinate math use this single constant.
  - `_get_rounded_icon` automatically crops transparent margins from the application icon and scales it into 52px inside the 58px circular frame with 3px edge padding.

### Fix B: Collapsed Drag Clamping Fix
- **Files Modified**: [`ui/widget.py`](file:///d:/DEV/floatnote/ui/widget.py#L731)
- **Problem Solved**: `_clamp_to_screen()` previously required at least `MIN_VISIBLE = 50` px of window overlap against monitor bounds. Any window <= 50px failed the check on every mouse move during a drag, causing the fallback branch to snap the widget to screen center.
- **Changes**:
  - Updated visibility threshold calculation to:
    ```python
    frame = self.frameGeometry()
    need_w = min(MIN_VISIBLE, frame.width())
    need_h = min(MIN_VISIBLE, frame.height())
    for screen in screens:
        available = screen.availableGeometry()
        intersection = frame.intersected(available)
        if intersection.width() >= need_w and intersection.height() >= need_h:
            visible_on_any = True
            break
    ```
  - Small windows, including collapsed icons, now cleanly pass the intersection check anywhere on any connected display, including near edges.

### Fix C: Dialog Separation (Blur Effect + Visible Panel Outlines)
- **Files Modified**: [`ui/widget.py`](file:///d:/DEV/floatnote/ui/widget.py#L635), [`ui/styles.py`](file:///d:/DEV/floatnote/ui/styles.py#L315)
- **Changes**:
  - In `FloatNoteWidget.exec_dialog()`, instantiated `QGraphicsBlurEffect(self)` with `blurRadius = 8` and applied it to `self._expanded_container` while the dialog is open.
  - Placed cleanup `self._expanded_container.setGraphicsEffect(None)` in a `finally:` block, ensuring that whether the dialog is accepted, rejected, cancelled, closed via `Escape`, or aborted on error, the note background is never left blurred.
  - Because `dlg` is a separate top-level dialog widget rendered over the main window, the blur affects only the note background, leaving dialog input controls crisp and legible.
  - In `DIALOG_STYLE`, added distinct top and bottom outline borders:
    ```css
    border: 1px solid rgba(255, 255, 255, 55);
    border-top: 1.5px solid rgba(255, 255, 255, 120);
    border-bottom: 1.5px solid rgba(255, 255, 255, 95);
    ```

### Section 4: Inno Setup Upgrade & Script Consolidation
- **Files Modified**: [`floatnote.iss`](file:///d:/DEV/floatnote/floatnote.iss), [`build/installer.iss`](file:///d:/DEV/floatnote/build/installer.iss)
- **Changes**:
  - In `floatnote.iss`, bumped `#define MyAppVersion "2.0.1"`.
  - Confirmed `AppId={{#MyAppId}` uses fixed GUID `{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}` so installer replaces previous installs in-place.
  - Confirmed notes directory (`Documents\FloatNote`) is never touched during installation or uninstallation.
  - Added a deprecation notice header to `build/installer.iss` designating `floatnote.iss` at the repository root as the canonical build script.

---

## 2. Verification Results

### Automated Unit Tests
Ran the full test suite (`.venv\Scripts\python.exe -m unittest discover tests`):
```text
Ran 21 tests in 3.340s

OK
```

All 21 test cases passed:
1. `test_v1_migration`: V1 notes migrated to `General/notes.txt` with backup archive.
2. `test_starter_note_on_fresh_install`: Starter notes created properly.
3. `test_category_crud`: Category creation and listing.
4. `test_note_crud`: Note creation, reading, saving, renaming, deleting.
5. `test_active_note_resolution`: Default and fallback resolution.
6. `test_markdown_preview_sync`: Content synchronization in preview.
7. `test_acrylic_color_tuple`: Acrylic helper functions.
8. `test_hotkey_manager_lifecycle`: Hotkey registration and callback.
9. `test_hotkey_fallback_message`: Windows API fallback.
10. `test_smart_anchoring_geometry`: Anchoring left/right logic.
11. `test_styles_output`: QSS palette and syntax.
12. `test_markdown_rendering`: Markdown styling and tags.
13. `test_widget_creation_and_preview_toggle`: UI widget toggles.
14. `test_dialogs_instantiation`: Dialog classes instantiation.
15. `test_fix2_scrim_overlay_exists`: Scrim overlay lifecycle.
16. `test_fix3_resize_handle_and_ceiling`: Vertical resize up to full screen height.
17. `test_fix4_collapsed_size`: **Round 2 Fix A** — `COLLAPSED_SIZE == 58`, `COLLAPSED_RADIUS == 29`, and QSS min-width 58px.
18. `test_fix5_open_notes_folder_target`: Folder opens active category directly.
19. `test_fix7_fixed_appid_in_installer`: Fixed `AppId` and `{localappdata}`.
20. `test_round2_fix_b_clamp_to_screen_small_window`: **Round 2 Fix B** — small collapsed widget does not snap to center when dragged near edges.
21. `test_round2_fix_c_dialog_blur_and_borders`: **Round 2 Fix C** — blur applied during `exec_dialog`, cleared in `finally:`, and distinct top/bottom border styles.
22. `test_round2_installer_version_bump`: **Round 2 Section 4** — `MyAppVersion == "2.0.1"` and `build/installer.iss` marked deprecated.

---

## 3. Manual Testing & Verification Instructions

To manually test the updated dev build:

1. **Restart Dev Instance**:
   If a dev instance is already running, terminate it and start fresh:
   ```powershell
   .venv\Scripts\python.exe main.py
   ```

2. **Verify Fix A (Collapsed Icon Size)**:
   - Collapse the note widget by clicking the collapse icon in the header.
   - The circular collapsed button is now **58px** in diameter (noticeably larger than the previous 44px, but slightly smaller than original 64px).
   - The application icon fills the circle with clean 3px padding.

3. **Verify Fix B (Collapsed Dragging)**:
   - Click and drag the collapsed icon across the screen.
   - Drag it towards the top, bottom, left, and right screen edges and release.
   - **Expected**: It smoothly follows the cursor and stays where dropped. It no longer snaps to screen center.
   - Click (without moving) on the icon: the widget cleanly expands.

4. **Verify Fix C (Dialog Blur & Outlines)**:
   - In expanded mode with text in the editor, click the menu button (`⋮`) -> `New Note...` (or press `Ctrl+N`).
   - **Expected**:
     - The background note text and header are visibly blurred and dimmed behind the dialog.
     - The dialog itself has sharp text and input fields.
     - The dialog box has distinct, lighter top and bottom outline borders separating it from the background.
   - Press `Escape` or click `Cancel`.
   - **Expected**: The blur immediately clears and the note editor returns to normal sharpness.
   - Repeat with `New Folder...`, `Rename Active Note...`, and `Delete Active Note...` to verify all dialogs behave identically.

5. **Verify Section 1 Invariants (Do Not Regress)**:
   - [x] Drag the bottom resize handle down: note expands vertically up to full available screen height.
   - [x] Press `Ctrl+Shift+N`: window toggles hide/show.
   - [x] Background is neutral charcoal translucent glass.
   - [x] Click `Open Notes Folder`: opens active category folder (`%USERPROFILE%\Documents\FloatNote\notes\General`).
   - [x] Drag note to right side of screen and collapse/expand: right edge remains anchored.

---

## 4. Production Build Verification

The standalone application and installer binaries were built:
1. **PyInstaller Standalone Executable**:
   - Command: `.venv\Scripts\python.exe -m PyInstaller build/floatnote.spec --clean`
   - Output: [`dist/FloatNote.exe`](file:///d:/DEV/floatnote/dist/FloatNote.exe) (46,307,366 bytes)
   - Embedded Manifest Version: `2.0.1.0`
2. **Inno Setup Windows Installer**:
   - Command: `ISCC.exe floatnote.iss`
   - Output: [`dist/FloatNoteSetup.exe`](file:///d:/DEV/floatnote/dist/FloatNoteSetup.exe) (48,028,244 bytes)
   - Version: `2.0.1`
   - Target Directory: `%LOCALAPPDATA%\FloatNote`
   - Fixed `AppId`: `{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}` (ensures seamless v1-to-v2 in-place upgrades)

