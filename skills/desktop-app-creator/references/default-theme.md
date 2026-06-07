# The default theme

The windowed default is a **real theme, not bare Tkinter**. The target user can't specify a design
and shouldn't have to — so the skill ships one opinionated, coherent look and applies the whole
package when the user accepts the default. "Modern desktop app" is the bar users expect now; an app
that doesn't clear it reads as broken even when it works.

**The recommended theme is this branded dark look, surfaced in the interview as "Dark."** There is no
separate "default theme" option for now — Dark *is* the default the skill applies. (An earlier draft was
light-first; Dark-as-default is the one knob to flip if that's ever revisited.) The "light" / "minimal"
theme options are the plainer alternatives for a user who explicitly overrides the default. Deviate from
this theme only when the user asked for something else and you recorded it in `AUTHORING.md`.

## The palette

Calibrated to **Claude's desktop look**: a warm dark-grey canvas, soft borders, and Claude's single
coral accent. Warm (a hint of brown in the grey), not the cold blue-black of default OS dark mode —
that warmth is what makes it read as designed and as recognizably Claude.

| Token              | Value       | Use                                                        |
|--------------------|-------------|------------------------------------------------------------|
| `canvas`           | `#1F1E1D`   | Window body background (warm near-black, Claude's deepest) |
| `header-band`      | `#262624`   | Title bar + header + table-header, one continuous shade — Claude's signature dark grey |
| `surface`          | `#30302E`   | Cards, rows, input fields raised off the canvas            |
| `surface-hover`    | `#3A3A37`   | Hover/active state on interactive surfaces                 |
| `border`           | `#423F3B`   | Soft 1px borders — visible but never harsh                 |
| `text`             | `#F5F4EE`   | Primary text (warm off-white, Claude's "Pampas", never pure `#FFF`) |
| `text-muted`       | `#B7B3A9`   | Secondary text, labels, timestamps                         |
| `accent`           | `#D97757`   | The single accent — Claude's coral; buttons, links, focus  |
| `accent-text`      | `#1F1E1D`   | Text on top of the accent                                  |
| `footer`           | `#8A8579`   | Footer attribution strip text                              |

One accent only — Claude's coral. Resist a second highlight color; the coherence comes from restraint.

## Text color — the bug that makes a dark app "still look light"

**Set `text` (or `text-muted`) as the explicit foreground on every text-bearing widget** — labels,
inputs, table cells, list rows, headers, buttons. Painting only the window/background dark is not
enough: a control that doesn't set its own foreground falls back to the OS default, which is **black
on a light-mode host**. The result is a dark window full of black, unreadable text that looks like
the light theme leaked through. This is the single most common dark-mode failure, so set foreground
everywhere, not just background.

- **Tkinter/PySide6:** set `fg`/`foreground` (and `insertbackground` for text-entry carets) on every
  widget and in the `ttk.Style`/Qt stylesheet — don't rely on widget defaults.
- **Web (Electron/Tauri):** set `color` on `body` and don't let any element reset it to a UA default;
  also set the `<meta name="color-scheme" content="dark">` so form controls render dark.
- **Native (AppKit/WinUI):** drive the appearance from the dark palette explicitly rather than
  letting the control inherit the system effective appearance.

## Typography

A **single system font** throughout — no font shopping, no bundled webfonts. Use the platform UI
font: `-apple-system`/SF on macOS, Segoe UI on Windows, the system default on Linux. One family,
two or three weights (regular for body, medium/semibold for headings and the header band). Size
steps roughly: 13px body, 12px muted/footer, 15–16px headings.

## Shape

- **Rounded corners on every container and control** — cards, buttons, inputs, the window itself
  where the framework allows. ~8px on containers, ~6px on controls. Nothing hard-cornered.
- Soft 1px `border` on raised surfaces; lean on the surface/canvas contrast more than on borders.
- Generous padding — let things breathe; cramped UI reads as unfinished.

## The header band — the rule that breaks most often

**Paint the title bar the same color as the body** (`header-band`), never the OS-default chrome
strip. The single most common tell of a "generated" app is a default grey/white OS title bar
sitting on top of a dark window. Don't ship that.

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
- [ ] Rounded corners on containers and controls.
- [ ] `text` foreground set explicitly on every label, input, cell, and header — no black-on-dark.
- [ ] One system font, one accent color (Claude coral).
- [ ] Footer attribution strip present and quiet.
- [ ] Outside text run through `html.unescape()` / `textContent`.
- [ ] Menu-bar app: chrome reapplied on every reopen.
