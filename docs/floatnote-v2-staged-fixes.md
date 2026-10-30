# FloatNote v2 — Staged Fixes (pre-release polish)

*Running list — add to this as more issues surface during v2 testing, then batch-hand to Antigravity once ready, same approach as the v2 PRD itself.*

## Fix 1 — Drop the blue tint, revert to v1's charcoal/gray palette

**Observed:** The v2 build's panel is genuinely translucent (confirmed — not an opacity/alpha problem after all), but the saturated blue tint itself is what reads as visually "solid" or heavy, unlike v1's lighter charcoal/gray glass.

**Fix direction:**
- Revert the panel color family from deep blue/indigo back to v1's neutral charcoal/gray tones
- Keep the translucency level as-is (it's already correct) — this is a hue change only, not an alpha change
- Applies to both the main expanded panel and the collapsed circular icon
- Note: this supersedes the earlier alpha-based diagnosis for this same issue — root cause was color choice, not transparency level

## Fix 2 — New-file dialog blends into note content

**Observed:** The "Create New Note" dialog overlays directly on top of the currently-open note, using a background shade close enough to the note panel's own color that dialog fields and note text visually merge — hard to read, feels like a rendering glitch rather than an intentional modal.

**Fix direction:**
- Give the dialog its own distinct visual treatment — either a noticeably different background shade/tone, or a border/shadow strong enough to read clearly as "a surface above the note," not the same surface
- Add a semi-opaque scrim/dim layer behind the dialog over the note content while it's open, the way standard modal dialogs separate themselves from the content behind them
- Applies to any similar popup/dialog going forward (new folder, rename, etc.) — same treatment should be used consistently

## Fix 3 — Drag-to-resize height regression (v1 feature missing in v2)

**Observed:** v1 supported dragging the bottom edge to adjust window height. v2 currently uses a fixed height with no resize handle — this needs to come back.

**Fix direction:**
- Restore the bottom-edge drag-to-resize behavior from v1 (same resize-handle approach, hover cursor, live height adjustment while dragging)
- **On the height ceiling:** v1 capped max height at 80% of the available screen height as an arbitrary safety limit. Recommendation: raise this to the **full available screen height** (i.e. up to the edge of the taskbar, using the screen's available-geometry height rather than a percentage of it) rather than keeping the 80% cap — there's no real reason to leave that headroom unused if someone wants a nearly full-height scratchpad. The window still can't exceed actual screen bounds either way, so "full available height" is a sensible practical ceiling rather than true removal of any limit.
- Keep the existing minimum-height floor as-is (prevents collapsing the note area to something unusably small)
- Persisted height (saved/restored between sessions) should continue to work the same way it did in v1

## Fix 4 — Collapsed icon has too much empty padding

**Observed:** The collapsed circular widget shows a lot of empty frame/padding around a small icon graphic inside it — the icon itself only fills a small portion of the available space.

**Fix direction:**
- Reduce the overall collapsed widget frame size by roughly 30%
- Increase the icon graphic size within that frame so it fills the space properly, removing the excess empty padding around it
- Net effect: a smaller, tighter collapsed widget where the icon is the dominant visual element, not a small icon floating in a mostly-empty frame

## Fix 5 — "Open Notes Folder" points to the wrong directory

**Observed:** Using the "Open Notes Folder" menu action opens the top-level app folder (`Documents\FloatNote`, containing `backups`, `notes`, `config.json`, etc.) rather than going straight into the actual notes subfolder. The user then has to manually navigate further in (into `notes\General` or whichever category).

**Fix direction:**
- "Open Notes Folder" should open directly into the relevant notes subfolder (e.g. `Documents\FloatNote\notes\<active category>`, or just `Documents\FloatNote\notes` if opening the active category specifically isn't feasible) — not the parent app-data folder
- The app's internal folders (`backups`, `config.json`) are implementation detail the user shouldn't need to see or navigate past just to get to their notes

## Fix 6 — Global hotkey (Ctrl+Shift+N) no longer works

**Observed:** The `Ctrl+Shift+N` show/hide hotkey that worked in v1 does not work in the v2 build — likely removed or broken during the v2 rework.

**Fix direction:**
- Restore working global hotkey behavior — same approach as v1 (native `RegisterHotKey` via `ctypes` with a message-only window, not the `keyboard` library)
- If v1's `core/hotkey.py` logic was carried over into v2 as-is, check whether something in the v2 changes (e.g. window lifecycle changes from multi-file support, or changes to how/when the app initializes) is preventing hotkey registration from running at startup, rather than assuming the hotkey code itself was deleted
- Verify the hotkey still works after collapse/expand and after switching between files, not just on a fresh launch

## Fix 7 — Installing v2 doesn't replace v1 (two instances end up installed)

**Observed:** Installing the v2 build alongside an existing v1 install results in two separate FloatNote instances/installs, rather than v2 replacing v1 as a proper upgrade.

**Likely cause:** Inno Setup determines whether an install is "the same app, new version" using a fixed `AppId` (GUID) in the `.iss` script. If v2's installer script was regenerated rather than reusing v1's exact `AppId` with just `AppVersion` bumped, Windows treats it as an entirely unrelated application — hence two separate Add/Remove Programs entries and two separate installs.

**Fix direction:**
- Ensure the `.iss` script uses a **permanently fixed `AppId`** that will never change across any future version — only `AppVersion` should increment per release
- With the correct `AppId`, installing v2 should detect the existing v1 install and upgrade/replace it automatically (standard Inno Setup upgrade behavior), rather than installing side-by-side
- **Data safety requirement:** the installer must only replace program files — it must never touch or delete the user's existing `Documents\FloatNote` folder (notes, backups, `config.json`). Verify this explicitly, since an upgrade that wipes existing notes would be far worse than the current side-by-side bug
- If two installations already exist from this testing round, both will likely need to be manually uninstalled once before testing the corrected installer, since neither one currently "knows about" the other
