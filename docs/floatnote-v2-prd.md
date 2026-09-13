# FloatNote v2 — Product Requirements Document

**Status:** Final draft — ready for implementation
**Platform:** Windows 10/11 desktop
**Prior version:** v1 shipped, in daily use, stable
**Target implementer:** Antigravity (AI coding agent)

---

## 1. Overview

FloatNote is a lightweight, always-on-top desktop widget for jotting quick notes while working or browsing. v1 delivered a single-note scratchpad experience: collapsible, glass-styled, hotkey-toggled, and installable as a standalone Windows app. v2 evolves it from a single-note tool into a lightweight multi-file notes widget, while keeping the core "stays out of the way, always reachable" philosophy intact.

This document assumes v1's foundation (frameless window, acrylic rendering, global hotkey, system tray, installer/uninstaller pipeline) is working and stable, and specifies what changes and what's added for v2.

## 2. Goals for v2

1. Support multiple notes/files instead of a single persistent note
2. Let the user browse, organize, and switch between files via a menu
3. Support Markdown files with real rendering/preview, not just plain text saved with a `.md` extension
4. Fix the expand/collapse positioning bug (widget can get pushed off-screen when docked on the right side)
5. Apply the previously-deferred visual restyle to the main app UI
6. Fold in any other polish/bug fixes surfaced from v1 daily use

## 3. Non-Goals for v2

- No cloud sync — local file storage only, same as v1
- No collaborative/multi-user features
- No mobile companion app
- The flagging/badge-count feature (see Section 8, v2.1) is explicitly **out of scope for v2** — do not implement it in this pass

## 4. Feature Specifications

### 4.1 Multi-File Support
- Replace the single hardcoded `notes.txt` model with support for multiple independent note files.
- **File creation flow:** when the user creates a new file, prompt them for a name at creation time (a simple text-input dialog). Do not auto-generate names silently.
- **Migration:** on first v2 launch, if an existing v1 `notes.txt` is present, migrate it automatically into the new multi-file structure as the user's first file (preserve its content, don't discard it or ask the user to re-save it).
- Each file auto-saves independently using the same debounce-on-edit approach as v1 (~500ms after last keystroke, not on every keystroke).

### 4.2 File Organization — Folders/Categories
- The storage and file-menu model must support **folders/categories**, not just a flat list of files.
- Users should be able to create a folder/category and assign files to it (either at file-creation time, or by moving/assigning after the fact — pick whichever is simpler to implement well, but a file must always belong to some category, even if that's an "Uncategorized" default).
- The file-menu UI (Section 4.3) needs to reflect this folder structure, not just dump every file into one list.

### 4.3 File Menu
- Add a menu accessible from the widget (e.g. a header button, or integrated into the existing tray context menu — implementer's choice, but it must be reachable without leaving the widget's normal always-on-top workflow) that:
  - Shows folders/categories, and the files within each
  - Lets the user open an existing file (loads it into the note editor, replacing the current view)
  - Lets the user create a new file (triggers the name-prompt flow from 4.1)
  - Lets the user create a new folder/category
- The widget should remember which file was last open and reopen it on next launch, same as v1's single-file persistence behavior.

### 4.4 Markdown Support (with rendering)
- Files can be created and opened as Markdown (`.md`).
- **This must include actual rendering/preview of Markdown formatting** (headers, bold, italics, lists, etc.) — not just plain-text editing of files that happen to have a `.md` extension.
- Given the widget's fixed ~288px width, design the rendering/preview approach to work within that constraint — e.g. a toggle between raw-edit and rendered-preview mode, or inline live rendering, whichever fits better once in development. Flag any width-related rendering compromises back for review rather than silently shrinking text to illegible sizes.
- Plain `.txt` files remain supported exactly as in v1 (no rendering needed for those).

### 4.5 Smart Expand/Collapse Anchoring
- **Bug being fixed:** currently, expanding from the collapsed icon always grows the window rightward and downward from a fixed top-left point. When the widget is docked near the right edge of the screen, this pushes the expanded window off-screen, requiring the user to manually drag it back.
- **Required behavior:** before expanding or collapsing, determine which side of the screen the widget currently occupies (compare its horizontal position against the available screen width — e.g. whichever screen edge it's closer to).
  - If on the **left side** of the screen: keep the current behavior — anchor the top-left corner, expand rightward/downward.
  - If on the **right side** of the screen: anchor the top-right corner instead — expand leftward/downward, and when collapsing, shrink back toward that same top-right point.
- This should work per-instance at expand/collapse time (i.e. re-evaluate position each time, since the user may have moved the widget between collapses).
- Apply the same on-screen clamping logic v1 already has (never allow the widget to end up fully off-screen after a monitor change) — this feature works alongside that, not instead of it.

### 4.6 Visual Restyle — Deep-Blue Glossy Glass
- Update the app's UI styling (the main panel, the collapsed circular icon, borders/accents) from the current neutral dark-gray glass look to a **glossy, saturated deep-blue glass** aesthetic:
  - Rounded glass panels with a bright, thin rim-light highlight along the top-left edge
  - A soft interior glow
  - A rich, saturated dark-blue/indigo tint rather than neutral gray
  - Update both the QSS-fallback styling and the native acrylic tint color (if the acrylic implementation accepts a tint parameter) so both rendering paths match
- **Important — keep this separate from the app icon:** the app's `.ico` (taskbar/tray/shortcut icon) uses a different purple/gold illustrated style and should **not** be changed to match this blue theme. The in-app UI glass color and the icon's color are intentionally two separate aesthetics — do not attempt to unify them.
- Do not change layout, spacing, fonts, or button sizing as part of this — visual/color pass only.

### 4.7 General Polish Pass
- Before considering v2 complete, do a pass over general day-to-day usage friction from v1 and fix anything reasonable within scope (implementer should flag anything ambiguous rather than guessing at undocumented "polish" requests).

## 5. Explicitly Deferred — v2.1 (Do Not Build Yet)

- **Flagging/marking whole files**, with a notification-style numeric badge (like a mobile app's unread count) showing how many files are flagged.
  - Badge renders on the **collapsed circular icon only** — not on the system tray icon.
  - Flag is a whole-file property, not per-line/per-section.
  - This depends on multi-file support (Section 4.1) existing first, which is why it's v2.1 rather than v2 — but it should **not** be implemented in this v2 pass. Listed here only for context/future planning.

## 6. Technical Notes Carried Over From v1

- Stack: Python, PySide6 (LGPL — intentional choice over PyQt6 for redistribution)
- Native Windows integration via `ctypes`: DWM acrylic effect, global hotkey (`RegisterHotKey`, not the `keyboard` library), startup registry entry
- Packaging: PyInstaller (single-file build) + Inno Setup (installer/uninstaller)
- These should remain unchanged in v2 — no stack migration as part of this version (a C#/WinUI rewrite was considered and explicitly deferred; do not revisit in this pass)

## 7. Success Criteria for v2

- Existing v1 users' notes migrate automatically and are not lost on upgrade
- Multiple files can be created, named, organized into folders, and switched between without data loss
- Markdown files render formatting correctly within the widget's constraints
- The widget never requires manual dragging after expand/collapse regardless of which side of the screen it's docked on
- The restyled UI uses the deep-blue glass theme consistently across all states (expanded, collapsed) while the app icon remains untouched
- No regressions to v1's stable behavior (drag, resize, hotkey, tray menu, click-through fix, startup toggle)

## 8. Open Items for Implementer

None outstanding — all major decisions (naming flow, folder support, Markdown rendering scope, icon/UI color separation) have been resolved as specified above. If a genuine ambiguity comes up during implementation that isn't covered here, flag it for review rather than assuming.
