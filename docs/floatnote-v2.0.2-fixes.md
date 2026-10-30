# FloatNote v2.0.2 — Bug Fix Handoff

**Release type:** Patch (bug fixes only, no new features)
**Applies on top of:** v2.0.1
**This document is self-contained.** It lists only the open items for this release. Earlier fix documents are archived and should not be used.

---

## 1. Do Not Regress (shipped in v2.0.1)

Spot-check these after every change below:

- Vertical drag-to-resize, with the maximum height up to the full available screen height
- `Ctrl+Shift+N` global hotkey
- Charcoal/gray translucent background
- "Open Notes Folder" opening the notes subfolder directly
- Smart expand/collapse anchoring (left side expands rightward, right side expands leftward)
- Collapsed icon (about 58px) can be dragged anywhere and never snaps to center
- Dialogs show a blurred note behind them with visible top and bottom borders
- Installer keeps its fixed `AppId`, the versioned filename, and never touches `Documents\FloatNote`

---

## 2. Fixes To Make

### Fix 1 — Deleting a note has no effect (confirmed cause)

**Observed:** Choosing "Delete Active Note…" and confirming appears to do nothing: the note is still there afterward.

**Root cause (`ui/widget.py`, `core/storage.py`):** `_delete_active_note()` deletes the file with `storage.delete_note()`, then calls `switch_to_note()`. `switch_to_note()` always starts with `self.flush_pending_save()`, which always calls `_flush_save()`. That writes the editor's current text to `self._active_category / self._active_note`, which is still the note that was just deleted. `storage.save_note()` creates the file unconditionally, so the deleted note is written straight back to disk. `resolve_active_note()` then finds it again and returns it, so the user stays on the "deleted" note.

**Required fix:**
- Add a `flush` parameter: `switch_to_note(self, category, filename, flush=True)`, and skip the flush when it is `False`
- In `_delete_active_note()`, stop the pending autosave timer before deleting (`self._save_timer.stop()`), and call `switch_to_note(next_cat, next_note, flush=False)` afterward
- Check the return value of `storage.delete_note()`. If it returns `False`, show an error instead of silently continuing
- Make sure nothing else can write the deleted note back: closing the app right after a delete must not recreate it (the quit-time `flush_pending_save()` must target the new active note)
- Deleting the last remaining note currently makes `resolve_active_note()` create the starter welcome note. Keep that behavior, but confirm it is intended

**Verify:** Delete a note: it disappears from the menu and from disk, and the widget shows the next note. Type in a note and delete it within 500ms (before autosave fires): it still stays deleted. Delete, then quit and relaunch: it stays deleted.

### Fix 2 — Collapse/expand animation slides the content sideways on the right side of the screen (confirmed cause)

**Observed:** When the widget is on the right side of the screen, the text area appears to flip or slide to the right before collapsing. It feels like the left-side logic mirrored rather than a real anchored collapse.

**Root cause (`_run_collapse_animation` / `_on_animation_finished`):** The window is animated through its `geometry` property, but its size constraints are still locked while the animation runs. When expanded, the width is fixed at 288 and the minimum height is `MIN_HEIGHT`. When collapsed, the size is fixed at `COLLAPSED_SIZE` (min equals max). Qt clamps each animation frame to those limits, so the window cannot actually shrink or grow during the animation. Only the **position** animates. On the left side the x position barely changes, so the problem is hidden. On the right side the x position moves by about 240px, so the whole 288px-wide window visibly slides right and then snaps to the small size when the animation ends. Expanding on the right side is the reverse: a tiny icon slides left, then pops open.

**Required fix:**
- At the start of every collapse or expand animation, lift the size limits (`setMinimumSize(0, 0)` and `setMaximumSize(16777215, 16777215)`) so the geometry animation can really interpolate size and position together
- Keep the anchored corner fixed for the whole animation. On the right side, `x + width` must stay constant for every frame
- Do not let the note content visibly reflow or slide during the animation: hide the content (or crossfade it) while the window shrinks, and show it only once the window has reached its expanded size
- Reapply the final size limits in one place when the animation finishes. Create two helpers, `_apply_expanded_constraints()` and `_apply_collapsed_constraints()`, and use them from `initialize()`, `_on_animation_finished()`, and Fix 3's recovery check, so the constraint rules exist only once
- Keep the existing on-screen clamping and the 150ms duration

**Verify:** Collapse and expand on the far left, far right, and the middle of the screen. In all three, the content stays put, and on the right side the right edge never moves.

### Fix 3 — Widget width shrinks and needs a restart (cause not confirmed)

**Observed:** On one occasion the widget's overall size/width was smaller than it should be. A restart fixed it. The earlier collapsed-icon resizing (30%, then 10%) is a suspect.

**Likely area:** The size limits are changed in several places (`initialize()`, the animation-finished handler, collapse, expand). If an animation is interrupted or its finish handler runs at an unexpected moment (hotkey hide/show during an animation, monitor change, sleep/wake), the widget can be left with limits that belong to the other state. The fix for Fix 2 (single helpers, limits lifted during animation) removes the main way this can happen.

**Required:**
- Add `_enforce_size_invariants()`: based on `self._collapsed`, set the correct limits and size for that state. Call it when the widget is shown (including via the hotkey), when an animation finishes, and when the screen configuration changes
- Make sure the animation cannot be left half-finished: if the widget is hidden or the hotkey toggles mid-animation, finish the animation immediately to its end state
- Confirm no leftover hardcoded sizes remain from the earlier 30% and 10% icon changes. Every size must come from `FIXED_WIDTH` and `COLLAPSED_SIZE`
- Log a line whenever the widget's size does not match the expected size for its state, so the next occurrence can be diagnosed

### Fix 4 — Stale transparent layer left behind at an old height (cause not confirmed)

**Observed:** Once, the invisible layer under the widget (the one that was click-through in the original bug) stayed at the widget's previous, much taller height (about 80% of screen height) after the widget had been resized. It blocked clicks over that larger area. A restart fixed it. No screenshot was captured.

**Likely area:** With the translucent window and native backdrop, the native window rectangle and Qt's geometry can get out of sync when a resize happens while size limits are clamping it (the same limits problem as Fix 2 and Fix 3).

**Required:**
- On animation finish, on show, and after a drag-resize ends, compare Qt's geometry with the native window rectangle (`GetWindowRect` on the window handle). If they differ, log it and force them back in sync (re-set the geometry; if that is not enough, re-apply the acrylic effect)
- Do the mismatch check before attempting any other speculative fix, so the real cause is known
- Likely triggers to try reproducing: resize to maximum height then collapse and expand; hotkey toggling during an animation; dragging across monitors; display changes or sleep/wake

---

## 3. Acceptance Checklist

- [ ] Deleting a note removes it from disk and the menu, including after quit and relaunch, and when deleted within 500ms of typing
- [ ] Collapse and expand on the far left, middle, and far right of the screen show no sideways sliding of the content, and the anchored edge never moves
- [ ] Rapid hotkey toggling during animations never leaves the widget with the wrong size
- [ ] Size-mismatch and geometry-mismatch logging is in place for Fix 3 and Fix 4
- [ ] All items in Section 1 still work

---

## 4. Release Notes

- Bump `AppVersion` to 2.0.2. The installer file becomes `FloatNoteSetup-2.0.2.exe`
- `AppId` must not change
