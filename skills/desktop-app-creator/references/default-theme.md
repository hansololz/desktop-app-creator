# The default theme

The windowed default is a **real theme, not bare Tkinter**. The target user can't specify a design
and shouldn't have to — so the skill ships one opinionated, coherent look and applies the whole
package when the user accepts the default. "Modern desktop app" is the bar users expect now; an app
that doesn't clear it reads as broken even when it works.

**The default is dark-first for now.** (An earlier draft was light-first; this is the one knob to
flip if that's ever revisited.) The "light" / "dark" / "minimal" theme options are the plainer
alternatives for a user who explicitly overrides the default. Deviate from this theme only when the
user asked for something else and you recorded it in `AUTHORING.md`.

## The palette

A warm near-black canvas, soft borders, a single accent. Warm (a hint of brown/red in the black),
not the cold blue-black of default OS dark mode — that warmth is what makes it read as designed.

| Token              | Value       | Use                                                        |
|--------------------|-------------|------------------------------------------------------------|
| `canvas`           | `#1A1714`   | Window body background (warm near-black)                   |
| `header-band`      | `#211D19`   | Title bar + header + table-header, one continuous shade    |
| `surface`          | `#262220`   | Cards, rows, input fields raised off the canvas            |
| `surface-hover`    | `#2F2A27`   | Hover/active state on interactive surfaces                 |
| `border`           | `#3A3531`   | Soft 1px borders — visible but never harsh                 |
| `text`             | `#EDE8E2`   | Primary text (warm off-white, never pure `#FFF`)           |
| `text-muted`       | `#A39B92`   | Secondary text, labels, timestamps                         |
| `accent`           | `#E8975A`   | The single accent — warm amber; buttons, links, focus      |
| `accent-text`      | `#1A1714`   | Text on top of the accent                                  |
| `footer`           | `#8A8077`   | Footer attribution strip text                              |

One accent only. Resist a second highlight color — the coherence comes from restraint.

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
- [ ] One system font, one accent color.
- [ ] Footer attribution strip present and quiet.
- [ ] Outside text run through `html.unescape()` / `textContent`.
- [ ] Menu-bar app: chrome reapplied on every reopen.
