# Wayland Mirror GUI

[🇺🇸 English](README.md) | [🇺🇦 Українська](README_UA.md)

A simple yet very powerful graphical utility for screen mirroring on Wayland. Created specifically for those who miss a convenient "Windows-like" interface for configuring multiple monitors.

## Features
* **Native Mirroring (Zero-copy):** Uses `wlr-randr` for perfect pixel-by-pixel scaling without any performance loss or latency.
* **Windowed Mirroring:** Integration with `wl-mirror` to output the screen into a convenient window (useful for streaming or previews).
* **Modern & Compact Interface:** Screen selection is hidden inside sleek dropdown menus with checkboxes — perfect symmetry and nothing extra on the screen.
* **Multi-monitor Support:** Ability to broadcast one screen to multiple TVs or projectors simultaneously.
* **"Smart" Checkboxes:** Instantly enable or disable a broadcast on the fly simply by unchecking a box — no need to stop the entire session.
* **Dual Language & Memory:** The application supports English and Ukrainian. The selected language is saved automatically (defaults to English to be accessible to everyone).
* **Smart Position Memory:** Before mirroring, the program remembers the exact coordinates of the external monitor. When mirroring is canceled, it automatically restores the monitor to its exact previous location.
* **Auto-detection:** The program automatically detects which screens are currently mirrored (including `wl-mirror` windows) and syncs with the system state even after a restart.

## Requirements (Dependencies)
The following packages are required for the program to work:
* `python3`
* `python3-gi` (PyGObject for GTK3 interface support)
* `wlr-randr` (for native mirroring)
* `wl-mirror` (for windowed mirroring)

> [!WARNING]
> **Compatibility:** Native mirroring only works on true `wlroots`-based compositors (e.g., Sway, Wayfire, River, Labwc, MangoWM). It will **NOT work** on modern versions of Hyprland (as the developer dropped support for the `wlr-randr` protocol), nor on GNOME or KDE Plasma. However, the "Windowed mirroring" (`wl-mirror`) feature will still work on Hyprland without issues.

## How to Run
Just execute the script:
```bash
python3 wayland-mirror.py
```

## How it works
Under the hood, it parses the output of `wlr-randr`. When mirroring, the program dynamically reads the coordinates of the source monitor and physically maps the target monitor to that exact position, applying hardware scaling. Furthermore, it records the original coordinates of the target monitor in `~/.config/wayland-mirror.json` so that when mirroring is canceled, it automatically restores the screen to its proper place.
Settings (chosen language and saved screen positions) are saved in `~/.config/wayland-mirror.json`.

---
*Note: Currently tested on single/dual monitor setups. Feedback and bug reports on 3+ monitor setups are highly appreciated in the **Issues** section!*
