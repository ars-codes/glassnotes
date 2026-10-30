# FloatNote v2 — Round 2 Fixes (Follow-ups to the First Fix Pass)

**Context:** The first batch of v2 fixes has been tested in dev mode (`.venv\Scripts\python.exe main.py`). Most of it works. This document covers only what still needs work. Read the "Do Not Regress" section first.

**Suggested release tag:** v2.0.1 (patch release; bump `AppVersion` accordingly, see Section 4)

---

## 1. Do Not Regress (verified working, leave as-is)

- Vertical drag-to-resize of the expanded widget (max height up to full available screen height)
- `Ctrl+Shift+N` global hotkey
- Charcoal/gray translucent background
- "Open Notes Folder" opening the notes subfolder directly
- Smart expand/collapse anchoring on left/right screen sides

After every change below, confirm these five still work.

---

## 2. Fixes To Make

### Fix A — Collapsed icon is too small (resize target changed)

**Observed:** The first pass shrank the collapsed icon by about 30%, which made it too small.

**Required:**
- Set the collapsed size to a **10% reduction from the original size**, not from the current one. The original `COLLAPSED_SIZE` was 64, so the target is **about 58px**.
- The icon graphic should still fill the frame with minimal empty padding (the padding problem from the first pass stays fixed).
- Every place that depends on the collapsed size must use the single `COLLAPSED_SIZE` constant: the fixed size, the rounded/circular mask, the icon size, the collapse/expand animation rectangles, and the smart-anchoring math. Do not leave a hardcoded value anywhere.

### Fix B — Collapsed icon can't be dragged (snaps to screen center)

**Observed:** In collapsed mode, any drag attempt snaps the widget to the center of the screen and it cannot be moved. Dragging works in expanded mode.

**Root cause (`ui/widget.py`):** `_clamp_to_screen()` requires at least `MIN_VISIBLE = 50` px of the window to overlap a screen, in **both** width and height. Every drag calls `move_window()`, which calls `_clamp_to_screen()`. When the collapsed size fell below 50px (the 30% cut took 64px to about 45px), the overlap can never reach 50px, so the check always fails. The fallback branch then recenters the widget on every drag event. The expanded window is far larger than 50px, so it passes the check and drags normally.

**Required fix:** Make the visibility threshold depend on the window's own size, so a small window can pass:

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

Do this in addition to Fix A. At about 58px the old check would pass again, but only by accident, and any size below 50px would bring the bug back.

**Verify:**
- Drag the collapsed icon to all four screen edges and confirm it stays where it is dropped
- A click without movement still expands the widget
- Position persists after restarting the app
- The off-screen safety net still works: with the saved position set to a disconnected monitor's coordinates, the widget is brought back on-screen

### Fix C — Dialog still blends into the note behind it

**Observed:** The new-file dialog is still visually too close to the note content behind it.

**Required:**
- **Blur the note content behind the dialog** while it is open. Suggested approach: apply a `QGraphicsBlurEffect` (radius around 8) to the expanded container (header and editor/preview), and remove it with `setGraphicsEffect(None)` when the dialog closes. Remove it on every close path (accept, reject, and Escape), so the note is never left blurred.
- Give the dialog panel a **clearly visible border along its top and bottom edges** (a thin, lighter outline), so the panel edge is unmistakable.
- Apply the same treatment to all four dialogs: new note, new folder, rename, and delete.
- Keep the dialog fields readable: the blur must never apply to the dialog itself.

---

## 3. Acceptance Checklist

- [ ] Collapsed icon is about 58px with the graphic filling the frame
- [ ] Collapsed icon drags smoothly to any position, including all four screen edges, and never snaps to center
- [ ] Clicking (not dragging) the collapsed icon still expands it
- [ ] Collapsed position persists across restarts
- [ ] Dialogs show a blurred note behind them and visible top and bottom borders, and the blur clears when they close
- [ ] All five items in Section 1 still work

---

## 4. Installer Upgrade Check (pending verification, no code change requested yet)

The first-pass fix for v1-to-v2 upgrades has not been tested yet. Please confirm the following in the Inno Setup script (`floatnote.iss`), and change something only if it is wrong:

- `AppId` is a fixed GUID and must never change in any future version. Only `AppVersion` changes per release. Bump it for this patch release.
- Installing over an existing install replaces it in place, with no second copy and no second entry in Add or Remove Programs.
- Upgrading and uninstalling never touch `Documents\FloatNote` (notes, backups, config).
- Note that the repo currently has `floatnote.iss` at the project root and another installer script under `build/`. Confirm which one is the real one and remove or clearly mark the stale one.

The person testing will uninstall all existing copies first, then install the new build over a fresh v1 to test the upgrade path.
