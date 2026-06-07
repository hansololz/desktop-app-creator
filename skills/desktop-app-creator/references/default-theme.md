# The default theme

The windowed default is a **real theme, not bare Tkinter**. The target user can't specify a design
and shouldn't have to — so the skill ships one opinionated, coherent look and applies the whole
package when the user accepts the default. "Modern desktop app" is the bar users expect now; an app
that doesn't clear it reads as broken even when it works.

**The recommended theme is this branded light look, surfaced in the interview as "Light."** There is no
separate "default theme" option for now — Light *is* the default the skill applies. (An earlier draft was
dark-first; Light-as-default is the one knob to flip if that's ever revisited.) The "dark" / "minimal"
theme options are the plainer alternatives for a user who explicitly overrides the default. Deviate from
this theme only when the user asked for something else and you recorded it in `AUTHORING.md`.

## Framework-agnostic by construction

The theme is defined as **tokens and shape rules, not framework code** — a palette of named colors, a
radius scale, and a few component conventions. That definition is the single source of truth; each
framework just *maps* to it. The same tokens produce the same look whether the app is SwiftUI, WinUI,
GTK/Qt, an Electron/Tauri webview, or Tkinter/PySide6. Don't bake the look into one toolkit's idioms;
read the tokens below and bind them to whatever the chosen framework calls "background color," "corner
radius," and "border." The per-framework notes in this file are *mappings*, not separate themes.

## The palette

Calibrated to **Claude's desktop look** — a warm paper/cream canvas and Claude's single coral accent —
with **Tailwind's warm-grey (stone) neutrals** for surfaces, borders, and muted text. Warm, not the
cold blue-greys of a generic light UI; that warmth is what makes it read as designed and as
recognizably Claude.

| Token              | Value       | Use                                                          |
|--------------------|-------------|--------------------------------------------------------------|
| `canvas`           | `#FAF9F5`   | Window body background (Claude's warm paper/cream)           |
| `header-band`      | `#F0EEE6`   | Title bar + header + table-header, one continuous warm band  |
| `surface`          | `#FFFFFF`   | Cards, rows, input fields raised off the canvas              |
| `surface-hover`    | `#F2F1EA`   | Hover/active state on interactive surfaces                   |
| `border`           | `#E4E2DA`   | Soft 1px borders — warm grey (~Tailwind stone-200), never harsh |
| `text`             | `#1F1E1D`   | Primary text (Claude's warm near-black ink, ~stone-900, never pure `#000`) |
| `text-muted`       | `#73706A`   | Secondary text, labels, timestamps (~Tailwind stone-500)    |
| `accent`           | `#D97757`   | The single accent — Claude's coral; buttons, links, focus   |
| `accent-hover`     | `#C2613E`   | Hover/pressed state on accent buttons                       |
| `accent-text`      | `#FFFFFF`   | Text on top of the accent                                   |
| `focus-ring`       | `#D97757` @ 40% | Focus ring around the focused control (coral, semi-transparent) |
| `footer`           | `#A8A49B`   | Footer attribution strip text                              |

One accent only — Claude's coral. Resist a second highlight color; the coherence comes from restraint.

## Background *and* foreground — the bug that makes a light app "still look dark"

**Set both the background and the `text` foreground explicitly on every widget, and force the window
to a light appearance.** Painting only the window background light is not enough: a control that
doesn't set its own colors falls back to the OS default, which on a **dark-mode host** is a dark
surface with light text. The result is a light window with dark patches and washed-out, low-contrast
text — an app that "doesn't actually look light." This is the most common light-theme failure, so set
colors everywhere and pin the appearance to light:

- **Tkinter/PySide6:** set `bg`/`background` *and* `fg`/`foreground` (and `insertbackground` for
  text-entry carets) on every widget and in the `ttk.Style`/Qt stylesheet — don't rely on widget
  defaults.
- **Web (Electron/Tauri):** set `background` and `color` on `body`, don't let any element reset them
  to a UA default, and set `<meta name="color-scheme" content="light">` so form controls render light.
- **Native (AppKit/WinUI):** drive the appearance from the light palette explicitly and pin the
  effective appearance to light (e.g. `NSApp.appearance = .aqua` / WinUI `RequestedTheme="Light"`)
  rather than letting controls inherit the system dark appearance.

## Typography

A **single system font** throughout — no font shopping, no bundled webfonts. Use the platform UI
font: `-apple-system`/SF on macOS, Segoe UI on Windows, the system default on Linux. One family,
two or three weights (regular for body, medium/semibold for headings and the header band). Size
steps roughly: 13px body, 12px muted/footer, 15–16px headings.

## Shape — Tailwind's radius, spacing, and components

Take the shape language straight from Tailwind so controls read as a modern, consistent component set:

- **Rounded corners on every container and control**, on Tailwind's radius scale: **~8px (`rounded-lg`)
  on containers** — cards, panels, the window itself where the framework allows — and **~6px
  (`rounded-md`) on controls** — buttons, inputs, selects. Small chips/badges ~4px (`rounded`).
  Nothing hard-cornered.
- **Elevation by soft shadow, not just borders.** A light theme has little surface/canvas contrast,
  so raised surfaces lean on a subtle shadow the way Tailwind's `shadow-sm` does — roughly
  `0 1px 2px rgba(0,0,0,0.05)` — plus a 1px `border`. (In a dark theme you'd lean on surface contrast;
  in light, lean on the shadow.)
- **Component conventions, Tailwind-style.** Primary button: solid `accent` fill, `accent-text` label,
  `accent-hover` on hover. Secondary button: `surface` fill, 1px `border`, `text` label. Input: `surface`
  fill, 1px `border`, and a `focus-ring` on focus. Keep them consistent across the app.
- **Generous padding** — let things breathe; cramped UI reads as unfinished. Tailwind's 4px spacing
  rhythm (8/12/16px gaps) is a good default.
- **Fill the window — body, table, and footer stretch to fit.** The app's content occupies the whole
  window and keeps doing so as the user resizes; a fixed-size layout pinned to the top-left that leaves
  dead canvas down the right side and along the bottom is the other dead giveaway of a generated app.
  The body owns the full client area, the main table/list takes the available width and grows its row
  area to the available height (scrolling within that area when rows overflow, not pushing the window
  taller), and the footer strip sits flush on the bottom edge rather than floating halfway up. The
  mapping is the framework's primary layout axis, not a hack: **web/webview** — a column flexbox on a
  full-height body (`height: 100vh`, body `flex` column, the table region `flex: 1` with its own
  `overflow: auto`, footer fixed-height); **SwiftUI** — `.frame(maxWidth: .infinity, maxHeight:
  .infinity)` on the content and a `List`/`Table` that expands, footer outside the scroll; **AppKit/
  WinUI** — autoresizing masks / `Grid` with a star-sized (`*`) content row and an auto row for the
  footer so the table row absorbs the slack; **Tkinter** — `grid` with `rowconfigure`/`columnconfigure`
  weight on the table cell and the toplevel, `sticky="nsew"`; **PySide6** — a `QVBoxLayout` where the
  table has an expanding size policy and the footer a fixed one. The rule of thumb: exactly one region
  (usually the table/list) absorbs extra space, everything else is fixed-height, and nothing leaves a
  margin of bare canvas at the window's edge.
- **Popup panels light-dismiss on an outside click.** Any transient panel the UI floats over its
  content — a settings flyout, a model picker, a filter dropdown, a small detail popover — closes when
  the user clicks anywhere outside it, the same affordance every modern desktop app has. Clicking the
  surrounding canvas dismisses the panel *without* committing a pending change (Escape does the same),
  so a user who opened a panel by mistake is never trapped in it hunting for a close button. This is the
  default for non-modal popups; reserve a click-trapping modal for the rare case where the user genuinely
  must decide before doing anything else (an unsaved-changes confirm), and even then give it an explicit
  Cancel. The mapping is one line per stack: **web/webview** — a full-window backdrop layer (or a
  `pointerdown` listener on `document`) that closes the panel and `stopPropagation()` on the panel itself
  so an inside click doesn't bubble out; **SwiftUI/AppKit** — `.popover`/`Menu`, or `NSPopover` in
  `.transient` behavior, both of which light-dismiss for free; **WinUI** — `Flyout`/`Popup` with
  `IsLightDismissEnabled="True"`; **Tkinter/PySide6** — bind the toplevel's `<FocusOut>` / a global
  click outside the panel's bounds to `withdraw()`/`close()`. Prefer the framework's built-in
  popover/flyout, which gives outside-click dismissal as a default rather than something you wire by hand.

## The header band — the rule that breaks most often

**Paint the title bar the same color as the body** (`header-band`), never the OS-default chrome
strip. The single most common tell of a "generated" app is a default grey/white OS title bar
sitting on top of the app window. Don't ship that.

Take it one step further where the app has a header row: paint the **title bar, the header, and the
table-header as one continuous "header band"** in `header-band`, so they read as a single piece of
chrome flowing from the window edge down into the content. No seams, no color change at the title
bar boundary.

- **Native (macOS/AppKit/SwiftUI):** use a unified/transparent title bar
  (`titlebarAppearsTransparent`, full-size content view) and paint behind it.
- **Native (Windows/WinUI):** extend content into the title bar
  (`ExtendsContentIntoTitleBar`) and brush it `header-band`.
- **Web (Electron/Tauri):** frameless or hidden-titlebar window with a custom drag region styled as
  the header band.
- **Tkinter/PySide6:** where a custom title bar isn't practical, at minimum match the window
  background and style the in-window header as the band; note the limitation in `<os>-specific.md`.

**For menu-bar / tray apps, reapply the window chrome on every reopen** — toggling the activation
policy to show a window drops the custom chrome otherwise, so the second open looks wrong unless you
re-set it.

## The footer attribution strip

A thin strip along the bottom of the main window in `footer` text on the `header-band` shade — a
small, quiet "Built with desktop-app-creator" (or the app's own line). Low-contrast, unobtrusive,
single line. It's a finishing touch that signals intentional design, not a banner.

## HTML entity decoding — the other thing that looks broken

Decode HTML entities at the point outside text enters the app, so the UI shows `Dave's "news"` and
not `Dave&#039;s &quot;news&quot;`:

- **Python:** `html.unescape(s)` on text pulled from feeds/HTTP before it's displayed or stored.
- **Webview (Electron/Tauri):** set `element.textContent = s`, never `element.innerHTML = s`, for
  untrusted text — this both decodes correctly and avoids an injection vector.

Garbled entities are a small bug that makes the whole app look unfinished, so it's worth getting
right at the boundary once.

## Quick checklist before you call a windowed app done

- [ ] Title bar painted `header-band`, not the OS default chrome strip.
- [ ] Title bar + header + table-header read as one continuous band.
- [ ] Rounded corners on containers (~8px) and controls (~6px); raised surfaces carry a soft shadow.
- [ ] Popup panels (settings, pickers, dropdowns, popovers) dismiss on an outside click and on Escape.
- [ ] Content fills the window — body/table/footer stretch to the edges and stay filled on resize, no dead canvas.
- [ ] Background *and* `text` foreground set explicitly on every label, input, cell, and header — no dark-on-light leak.
- [ ] Window appearance pinned to light so a dark-mode host can't bleed through.
- [ ] One system font, one accent color (Claude coral).
- [ ] Footer attribution strip present and quiet.
- [ ] Outside text run through `html.unescape()` / `textContent`.
- [ ] Menu-bar app: chrome reapplied on every reopen.
