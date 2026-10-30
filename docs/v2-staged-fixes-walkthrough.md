# FloatNote v2 — Staged Fixes Walkthrough & Next Steps

This document details **what was done** across all 7 staged fixes from [`docs/floatnote-v2-staged-fixes.md`](file:///d:/DEV/floatnote/docs/floatnote-v2-staged-fixes.md), followed by the exact step-by-step checklist of **what to do** to test, build, and verify the v2 release.

---

## Part 1: What Was Done

### Summary of Changed Files

| File | Fixes Addressed | Key Modifications |
| :--- | :--- | :--- |
| [`core/acrylic.py`](file:///d:/DEV/floatnote/core/acrylic.py) | Fix 1 | Replaced blue composition tint (`0x8A3C1914` / `0xCC3C1914`) with neutral charcoal (`0x8A141414` / `0xCC141414`). |
| [`ui/styles.py`](file:///d:/DEV/floatnote/ui/styles.py) | Fix 1, 3, 4 | Restored neutral charcoal translucent glass styling, fixed CSS double-brace `{{` syntax bug in resize handle and collapsed icon, and adjusted collapsed diameter to 44px. |
| [`ui/dialogs.py`](file:///d:/DEV/floatnote/ui/dialogs.py) | Fix 2 | Added `QGraphicsDropShadowEffect`, distinct elevated card background, crisp rim highlights, and high-contrast labels/inputs for all dialogs. |
| [`ui/widget.py`](file:///d:/DEV/floatnote/ui/widget.py) | Fix 2, 3, 4, 5 | Added `ScrimOverlay` with `exec_dialog()` dimming, restored drag-to-resize handle (8px) with full-screen height ceiling, reduced `COLLAPSED_SIZE` to 44 with cropped icon bounding rect, and redirected notes folder opening. |
| [`core/storage.py`](file:///d:/DEV/floatnote/core/storage.py) | Fix 5 | Added [`get_category_path()`](file:///d:/DEV/floatnote/core/storage.py#L168) to resolve paths directly under `notes/<category>`. |
| [`core/hotkey.py`](file:///d:/DEV/floatnote/core/hotkey.py) | Fix 6 | Added 10-attempt retry mechanism (`_schedule_retry`) and error logging for hotkey registration contention. |
| [`main.py`](file:///d:/DEV/floatnote/main.py) | Fix 5, 6 | Added single-instance named Win32 Mutex to prevent ghost instances, and connected tray notes folder action directly to active category folder. |
| [`floatnote.iss`](file:///d:/DEV/floatnote/floatnote.iss) | Fix 7 | Restored permanently fixed v1 `AppId` (`{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}`), `{localappdata}` target, `PrivilegesRequired=lowest`, `CloseApplications=yes`, and confirmed data safety for `Documents\FloatNote`. |
| [`build/installer.iss`](file:///d:/DEV/floatnote/build/installer.iss) | Fix 7 | Synced `CloseApplications=yes` and `RestartApplications=no` with root installer. |
| [`tests/test_v2.py`](file:///d:/DEV/floatnote/tests/test_v2.py) | Verification | Updated test suite to validate neutral charcoal palette, scrim overlay, resize handle height/ceiling, collapsed sizing, and installer AppId (18 tests passing). |

---

### Detailed Fix-by-Fix Breakdown

#### Fix 1 — Revert from deep blue to v1 charcoal/gray palette
- **Root Cause**: The saturated navy/blue tint in acrylic and stylesheet gradients made the widget feel heavy and opaque rather than light neutral glass.
- **Implementation**:
  - In `core/acrylic.py`, updated Win32 acrylic composition tint to `0x8A141414` (keeping alpha 0x8A / 54%, but setting R=G=B=0x14 for neutral charcoal).
  - In `ui/styles.py`, reverted `BASE_STYLE` and `FALLBACK_STYLE` to `rgba(32, 36, 44, ...)` with subtle light rim borders (`rgba(255, 255, 255, 22)`).
  - Neutralized button hover/press states, title color, and scrollbar handles (`rgba(255, 255, 255, 60)`).
  - Neutralized `COLLAPSED_STYLE` to charcoal radial gradient.

#### Fix 2 — New-file dialog separation & scrim overlay
- **Root Cause**: Modals opened with low-contrast background directly over note text with no depth cue or backdrop separation.
- **Implementation**:
  - Created `ScrimOverlay` in `ui/widget.py` that paints a smooth `rgba(0, 0, 0, 160)` rounded backdrop over the entire note widget.
  - Implemented `FloatNoteWidget.exec_dialog(dlg)` which displays and raises the scrim, centers the dialog, runs `dlg.exec()`, and hides the scrim in a `finally:` block.
  - Applied across `_create_new_note`, `_create_new_folder`, `_rename_active_note`, and `_delete_active_note`.
  - In `ui/dialogs.py`, added `QGraphicsDropShadowEffect` (blur 24px, color `rgba(0, 0, 0, 180)`), elevated card styling (`rgba(36, 40, 48, 252)`), crisp borders, and bright white titles.

#### Fix 3 — Drag-to-resize height regression restored
- **Root Cause**: `ui/styles.py` had raw double curly braces `{{` in non-f-string `RESIZE_HANDLE_STYLE`. Qt's CSS parser treated this as invalid syntax and discarded the rule, which left the handle widget with a height of 0px (`QRect(0, 576, 288, 0)`).
- **Implementation**:
  - Corrected QSS syntax in `ui/styles.py` to single braces `{` `}`.
  - In `ui/widget.py`, set explicit `setFixedHeight(RESIZE_HANDLE_HEIGHT)` (8px) on `ResizeHandle`.
  - In `FloatNoteWidget._max_height()`, replaced the arbitrary 80% cap with the **full available screen height** (`screen.availableGeometry().height()`).
  - Added live clamping in `_clamp_height()` to stop cleanly at the taskbar edge.

#### Fix 4 — Collapsed widget frame size & icon padding
- **Root Cause**: The `.ico` file had ~35% transparent padding baked into the bitmap, which sat inside an oversized 64px circular frame.
- **Implementation**:
  - Reduced `COLLAPSED_SIZE` from 64px to 44px (~30% smaller, border-radius 22px).
  - In `_get_rounded_icon()`, detected the non-transparent content bounding box of the icon and cropped the transparent margins, rendering the icon graphic tightly (with 3px padding from the circular rim) so it dominates the frame.

#### Fix 5 — "Open Notes Folder" directory target
- **Root Cause**: Menu and tray actions opened `Documents\FloatNote`, exposing internal app files (`config.json`, `backups/`) rather than the user's actual notes.
- **Implementation**:
  - Added `storage.get_category_path(category)` in `core/storage.py`.
  - In `ui/widget.py`, updated `open_notes_folder()` to resolve the active category path (e.g. `Documents\FloatNote\notes\General`) or fallback to `Documents\FloatNote\notes`.
  - In `main.py`, connected the tray menu action directly to `widget.open_notes_folder`.

#### Fix 6 — Global hotkey (Ctrl+Shift+N)
- **Root Cause**: Multiple running FloatNote processes (from the v1 and v2 dual-install bug) caused Win32 error 1409 (`ERROR_HOTKEY_ALREADY_REGISTERED`).
- **Implementation**:
  - In `core/hotkey.py`, added a 10-attempt periodic retry timer (`_schedule_retry`) in `GlobalHotkeyManager` to automatically retry registration if the hotkey is held during startup or app reload.
  - In `main.py`, added Win32 single-instance mutex enforcement (`acquire_single_instance`). If a FloatNote instance is already running, subsequent launches terminate cleanly.

#### Fix 7 — Installer upgrade replacement & data safety
- **Root Cause**: `floatnote.iss` used an ad-hoc AppId (`{D37F8A52-9A7B-4B6A-B7F2-7E1A613E99A1}`) and `{autopf}` (Program Files), while v1 used `{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}` and `{localappdata}`. Windows treated them as separate applications.
- **Implementation**:
  - Reverted `floatnote.iss` to use permanently fixed `AppId={{#MyAppId}` matching v1 (`{A7B3C4D5-E6F7-4890-ABCD-EF1234567890}`).
  - Set `DefaultDirName={localappdata}\{#MyAppName}` and `PrivilegesRequired=lowest`.
  - Added `CloseApplications=yes` and `RestartApplications=no`.
  - Verified data safety: `[Files]` and `[Code]` only touch `{app}` and registry Run key; `Documents\FloatNote` is never modified or deleted.

---

## Part 2: What To Do (Step-by-Step Action Guide)

Follow this checklist to test the changes locally, build the binary and installer, and verify the upgrade path.

### Step 1: Clean up existing dual-installations
Before testing the installer, ensure any conflicting test installations on your machine are removed (per line 70 of the staged fixes doc):

1. Close any running FloatNote instances:
   ```powershell
   Stop-Process -Name FloatNote -Force -ErrorAction SilentlyContinue
   ```
2. Open Windows **Settings $\rightarrow$ Apps $\rightarrow$ Installed Apps** (or `appwiz.cpl`).
3. Uninstall any existing "FloatNote" entries (both the Program Files version and the LocalAppData version).
4. Verify your notes remain intact at `%USERPROFILE%\Documents\FloatNote`.

---

### Step 2: Run the test suite
Run the unit tests to confirm all functionality passes:
```powershell
.venv\Scripts\python.exe -m unittest discover tests
```
*Expected: 18 tests passing with `OK`.*

---

### Step 3: Test locally in development mode
Launch FloatNote from source:
```powershell
.venv\Scripts\python.exe main.py
```

#### Visual & Functional Checklist:
- [ ] **Palette**: Notice the panel has returned to v1's neutral charcoal/gray translucent glass (no heavy blue tint).
- [ ] **Resize Handle**: Hover over the bottom 8px of the window; verify the vertical resize cursor appears. Drag downward all the way to the taskbar. Verify the height expands smoothly to the screen boundary and persists across restarts.
- [ ] **Collapsed Widget**: Click "−" in the header. Verify the circular widget is noticeably smaller (44px) and the icon fills the circle without excess empty space.
- [ ] **Dialog & Scrim**: Click the menu (`≡`) and choose **New Note** (or press `Ctrl+N`). Verify the note area behind the dialog dims with a dark scrim, and the dialog appears cleanly elevated with shadow and clear borders.
- [ ] **Open Notes Folder**: In the menu (`≡`), click **Open Notes Folder**. Verify File Explorer opens directly into `Documents\FloatNote\notes\<ActiveCategory>` (e.g. `General`), not the parent folder.
- [ ] **Global Hotkey**: Press `Ctrl+Shift+N` while focused on other windows. Verify FloatNote toggles between visible and hidden.

---

### Step 4: Build the production executable
Compile the PyInstaller bundle:
```powershell
.venv\Scripts\pyinstaller build/floatnote.spec
```
*Output: `dist\FloatNote.exe`*

---

### Step 5: Compile the Inno Setup installer
Compile the installer using Inno Setup 6:
```powershell
iscc floatnote.iss
```
*Output: `dist\FloatNoteSetup.exe`*

---

### Step 6: Verify the installer upgrade behavior
1. Run `dist\FloatNoteSetup.exe`.
2. Notice the installer installs to `%LOCALAPPDATA%\FloatNote` without requesting admin privileges.
3. Launch the app, create a note.
4. Run `dist\FloatNoteSetup.exe` again while FloatNote is running.
5. Notice Inno Setup closes the running app, upgrades the executable in-place, and finishes.
6. Check **Installed Apps** in Windows Settings: verify there is **only one** FloatNote entry.
7. Launch FloatNote: verify your notes and settings are 100% preserved.
