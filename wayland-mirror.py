#!/usr/bin/env python3
import gi
import subprocess
import os
import json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

CONFIG_FILE = os.path.expanduser("~/.config/wayland-mirror.json")

TRANSLATIONS = {
    "uk": {
        "title": "Wayland Mirror",
        "source_label": "<b>Джерело для нативного дублювання:</b>",
        "choose_source": "Оберіть джерело...",
        "target_label": "<b>Куди виводити (Нативно):</b>",
        "choose_target": "Оберіть екрани...",
        "mirror": "Дублювати",
        "cancel": "Відмінити",
        "wl_label": "<b>Дублювати у вікні (wl-mirror):</b>",
        "open_window": "Відкрити вікно...",
        "refresh": "Оновити",
        "close_app": "Закрити",
        "no_screens": "Немає екранів",
        "no_other_screens": "Немає інших екранів",
        "selected": "Вибрано",
        "opened": "Відкрито",
        "main_laptop": "Основний / Ноутбук"
    },
    "en": {
        "title": "Wayland Mirror",
        "source_label": "<b>Source for native mirroring:</b>",
        "choose_source": "Choose source...",
        "target_label": "<b>Target screens (Native):</b>",
        "choose_target": "Choose screens...",
        "mirror": "Mirror",
        "cancel": "Cancel",
        "wl_label": "<b>Windowed mirroring (wl-mirror):</b>",
        "open_window": "Open window...",
        "refresh": "Refresh",
        "close_app": "Close",
        "no_screens": "No screens",
        "no_other_screens": "No other screens",
        "selected": "Selected",
        "opened": "Opened",
        "main_laptop": "Main / Laptop"
    }
}

class WaylandMirrorGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Wayland Mirror")
        self.set_default_size(320, 200)
        self.set_border_width(15)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Запит до віконного менеджера (Hyprland/Sway) зробити вікно плаваючим
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_resizable(False)
        
        self.set_decorated(False)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press)
        
        self.config = self.load_config()
        self.current_lang = self.config.get("language", "en") # Default to "en"

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.add(vbox)

        # Source MenuButton
        self.title_source = Gtk.Label()
        self.title_source.set_use_markup(True)
        vbox.pack_start(self.title_source, False, False, 0)

        self.source_btn = Gtk.MenuButton()
        self.source_btn.set_halign(Gtk.Align.CENTER)
        self.source_btn.set_size_request(280, -1)
        
        self.source_popover = Gtk.Popover()
        self.source_btn.set_popover(self.source_popover)
        
        self.source_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.source_box.set_border_width(10)
        self.source_popover.add(self.source_box)
        
        self._active_source_id = "none"
        vbox.pack_start(self.source_btn, False, False, 5)

        self._is_populating = False

        # Target MenuButton
        self.title_target = Gtk.Label()
        self.title_target.set_use_markup(True)
        vbox.pack_start(self.title_target, False, False, 0)

        self.target_btn = Gtk.MenuButton()
        self.target_btn.set_halign(Gtk.Align.CENTER)
        self.target_btn.set_size_request(280, -1)
        
        self.target_popover = Gtk.Popover()
        self.target_btn.set_popover(self.target_popover)
        
        self.target_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.target_box.set_border_width(10)
        self.target_popover.add(self.target_box)
        
        self.target_checkboxes = {}
        vbox.pack_start(self.target_btn, False, False, 5)

        # Grid for Native Action Buttons
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_column_homogeneous(True)
        vbox.pack_start(grid, False, False, 5)

        self.mirror_btn = Gtk.Button()
        self.mirror_btn.connect("clicked", self.on_native_mirror_clicked)
        grid.attach(self.mirror_btn, 0, 0, 1, 1)

        self.stop_native_btn = Gtk.Button()
        self.stop_native_btn.connect("clicked", self.on_stop_native_clicked)
        self.stop_native_btn.set_sensitive(False)
        grid.attach(self.stop_native_btn, 1, 0, 1, 1)

        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep, False, False, 5)

        # Windowed mirror section
        self.title_wl = Gtk.Label()
        self.title_wl.set_use_markup(True)
        vbox.pack_start(self.title_wl, False, False, 0)
        
        self.wl_btn = Gtk.MenuButton()
        self.wl_btn.set_halign(Gtk.Align.FILL)
        
        self.wl_popover = Gtk.Popover()
        self.wl_btn.set_popover(self.wl_popover)
        
        self.wl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.wl_box.set_border_width(10)
        self.wl_popover.add(self.wl_box)
        
        self.wl_checkboxes = {}
        
        wl_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        wl_hbox.set_halign(Gtk.Align.CENTER)
        wl_hbox.set_size_request(280, -1)
        vbox.pack_start(wl_hbox, False, False, 5)
        
        wl_hbox.pack_start(self.wl_btn, True, True, 0)
        
        self.stop_wl_btn = Gtk.Button()
        self.stop_wl_btn.connect("clicked", self.on_stop_wl_clicked)
        self.stop_wl_btn.set_sensitive(False)
        wl_hbox.pack_start(self.stop_wl_btn, False, False, 0)

        # Close button box & Language Selector
        close_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        close_box.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(close_box, False, False, 15)
        
        self.lang_combo = Gtk.ComboBoxText()
        self.lang_combo.append("en", "EN")
        self.lang_combo.append("uk", "UA")
        self.lang_combo.set_active_id(self.current_lang)
        self.lang_combo.connect("changed", self.on_lang_changed)
        self.lang_combo.set_margin_end(30)
        close_box.pack_start(self.lang_combo, False, False, 0)

        self.refresh_btn = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        self.refresh_btn.set_image(refresh_icon)
        self.refresh_btn.set_always_show_image(True)
        self.refresh_btn.connect("clicked", self.on_refresh_clicked)
        close_box.pack_start(self.refresh_btn, False, False, 0)

        self.close_btn = Gtk.Button()
        self.close_btn.connect("clicked", Gtk.main_quit)
        close_box.pack_start(self.close_btn, False, False, 0)

        # Apply translations and populate
        self.update_static_labels()
        outputs = self.get_outputs()
        self.populate_lists(outputs)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        
        self.check_current_state()

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self, key, value):
        self.config[key] = value
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f)
        except Exception:
            pass

    def t(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def on_lang_changed(self, combo):
        new_lang = combo.get_active_id()
        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            self.save_config("language", new_lang)
            self.update_static_labels()
            self.on_refresh_clicked(None)

    def update_static_labels(self):
        self.title_source.set_markup(self.t("source_label"))
        self.title_target.set_markup(self.t("target_label"))
        self.title_wl.set_markup(self.t("wl_label"))
        
        self.mirror_btn.set_label(self.t("mirror"))
        self.stop_native_btn.set_label(self.t("cancel"))
        self.stop_wl_btn.set_label(self.t("cancel"))
        self.refresh_btn.set_label(self.t("refresh"))
        self.close_btn.set_label(self.t("close_app"))
        
        # Source dropdown text
        if self._active_source_id == "none" or not self._active_source_id:
            self.source_btn.set_label(self.t("choose_source"))
            
        self.update_target_btn_label()
        self.update_wl_btn_label()

    def get_source_id(self):
        return self._active_source_id
        
    def set_source_id(self, source_id, display_name=None):
        self._active_source_id = source_id
        if source_id == "none" or not source_id:
            self.source_btn.set_label(self.t("choose_source"))
        else:
            if display_name:
                self.source_btn.set_label(display_name)
            else:
                self.source_btn.set_label(source_id)
                
        self._is_populating = True
        visible_count = 0
        for tgt_id, cb in getattr(self, "target_checkboxes", {}).items():
            if tgt_id == source_id:
                if cb.get_active():
                    cb.set_active(False)
                cb.set_visible(False)
            else:
                cb.set_visible(True)
                visible_count += 1
                
        if hasattr(self, "no_targets_label"):
            self.no_targets_label.set_visible(visible_count == 0)
            
        self._is_populating = False

    def on_source_clicked(self, widget, source_id, display_name):
        self.set_source_id(source_id, display_name)
        self.source_popover.popdown()

    def on_button_press(self, widget, event):
        if self.target_popover.is_visible():
            self.target_popover.popdown()
        if self.wl_popover.is_visible():
            self.wl_popover.popdown()
        if self.source_popover.is_visible():
            self.source_popover.popdown()
            
        if event.button == 1:
            self.begin_move_drag(event.button, event.x_root, event.y_root, event.time)
            return True
        return False

    def update_target_btn_label(self, widget=None):
        targets = self.get_selected_targets()
        if not targets:
            self.target_btn.set_label(self.t("choose_target"))
        elif len(targets) == 1:
            self.target_btn.set_label(targets[0])
        else:
            self.target_btn.set_label(f"{self.t('selected')} ({len(targets)})")

        if widget is not None and not getattr(self, "_is_populating", False):
            target = None
            for name, cb in self.target_checkboxes.items():
                if cb == widget:
                    target = name
                    break
            source = self.get_source_id()
            if source and source != "none" and target:
                if widget.get_active():
                    if self.mirror_btn.get_style_context().has_class("suggested-action"):
                        source_w, source_h = self.get_output_resolution(source)
                        target_w, target_h = self.get_output_resolution(target)
                        source_pos_x, source_pos_y = self.get_output_pos(source)
                        pos_str = f"{source_pos_x},{source_pos_y}"
                        
                        target_pos_x, target_pos_y = self.get_output_pos(target)
                        target_pos_str = f"{target_pos_x},{target_pos_y}"
                        saved_positions = self.config.get("saved_positions", {})
                        if target_pos_str != pos_str:
                            saved_positions[target] = target_pos_str
                            self.save_config("saved_positions", saved_positions)
                            
                        if source_w and target_w:
                            scale = target_w / source_w
                            subprocess.run(["wlr-randr", "--output", target, "--scale", str(scale), "--pos", pos_str])
                        else:
                            subprocess.run(["wlr-randr", "--output", target, "--pos", pos_str])
                else:
                    saved_positions = self.config.get("saved_positions", {})
                    pos = saved_positions.get(target)
                    if pos:
                        subprocess.run(["wlr-randr", "--output", target, "--pos", pos, "--scale", "1"])
                    else:
                        subprocess.run(["wlr-randr", "--output", target, "--right-of", source, "--scale", "1"])
                    if not targets:
                        self.mirror_btn.get_style_context().remove_class("suggested-action")
                        self.stop_native_btn.set_sensitive(False)

    def populate_lists(self, outputs):
        self._is_populating = True
        
        for child in self.source_box.get_children():
            self.source_box.remove(child)
        for child in self.target_box.get_children():
            self.target_box.remove(child)
        self.target_checkboxes.clear()
        for child in self.wl_box.get_children():
            self.wl_box.remove(child)
        self.wl_checkboxes.clear()
        
        if not outputs:
            self.source_box.pack_start(Gtk.Label(label=self.t("no_screens")), False, False, 0)
            self.target_box.pack_start(Gtk.Label(label=self.t("no_screens")), False, False, 0)
            self.wl_box.pack_start(Gtk.Label(label=self.t("no_screens")), False, False, 0)
        else:
            self.no_targets_label = Gtk.Label(label=self.t("no_other_screens"))
            self.target_box.pack_start(self.no_targets_label, False, False, 0)
            
            for out, display_name in outputs.items():
                s_btn = Gtk.Button(label=display_name)
                s_btn.connect("clicked", self.on_source_clicked, out, display_name)
                self.source_box.pack_start(s_btn, False, False, 0)
                
                cb = Gtk.CheckButton(label=display_name)
                cb.connect("toggled", self.update_target_btn_label)
                self.target_box.pack_start(cb, False, False, 0)
                self.target_checkboxes[out] = cb
                
                wl_cb = Gtk.CheckButton(label=display_name)
                wl_cb.connect("toggled", self.on_wl_toggled, out)
                self.wl_box.pack_start(wl_cb, False, False, 0)
                self.wl_checkboxes[out] = wl_cb
                
        self.source_box.show_all()
        self.target_box.show_all()
        self.wl_box.show_all()
        
        source = self.get_source_id()
        visible_count = 0
        for tgt_id, cb in self.target_checkboxes.items():
            if tgt_id == source:
                cb.set_visible(False)
            else:
                visible_count += 1
        if hasattr(self, "no_targets_label"):
            self.no_targets_label.set_visible(visible_count == 0)
            
        self.update_target_btn_label()
        self.update_wl_btn_label()
        self._is_populating = False

    def update_wl_btn_label(self):
        active_count = sum(1 for cb in self.wl_checkboxes.values() if cb.get_active())
        if active_count == 0:
            self.wl_btn.set_label(self.t("open_window"))
            self.wl_btn.get_style_context().remove_class("suggested-action")
            self.stop_wl_btn.set_sensitive(False)
        elif active_count == 1:
            active_name = [name for name, cb in self.wl_checkboxes.items() if cb.get_active()][0]
            self.wl_btn.set_label(active_name)
            self.wl_btn.get_style_context().add_class("suggested-action")
            self.stop_wl_btn.set_sensitive(True)
        else:
            self.wl_btn.set_label(f"{self.t('opened')} ({active_count})")
            self.wl_btn.get_style_context().add_class("suggested-action")
            self.stop_wl_btn.set_sensitive(True)

    def on_wl_toggled(self, widget, output_id):
        self.update_wl_btn_label()
        if getattr(self, "_is_populating", False):
            return
            
        if widget.get_active():
            subprocess.Popen(["wl-mirror", output_id])
        else:
            try:
                res = subprocess.run(["pgrep", "wl-mirror"], capture_output=True, text=True)
                if res.returncode == 0:
                    for pid in res.stdout.splitlines():
                        pid = pid.strip()
                        if pid:
                            try:
                                with open(f"/proc/{pid}/cmdline", "r") as f:
                                    cmd = f.read().split('\0')
                                    if len(cmd) >= 2 and cmd[-2] == output_id:
                                        subprocess.run(["kill", pid])
                            except Exception:
                                pass
            except Exception:
                pass

    def on_stop_wl_clicked(self, widget):
        for name, cb in self.wl_checkboxes.items():
            if cb.get_active():
                cb.set_active(False)
        self.wl_popover.popdown()

    def get_selected_targets(self):
        targets = []
        for name, cb in self.target_checkboxes.items():
            if cb.get_active():
                targets.append(name)
        return targets

    def get_outputs(self):
        outputs = {}
        try:
            res = subprocess.run(["wlr-randr"], capture_output=True, text=True)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if not line.startswith(" ") and line.strip():
                        parts = line.split('"', 1)
                        name = parts[0].strip()
                        if name.startswith("eDP") or name.startswith("LVDS") or name.startswith("DSI"):
                            outputs[name] = f"{name} ({self.t('main_laptop')})"
                        else:
                            if len(parts) > 1:
                                desc = parts[1].rsplit('"', 1)[0].strip()
                                if len(desc) > 20:
                                    desc = desc[:17] + "..."
                                outputs[name] = f"{name} ({desc})"
                            else:
                                outputs[name] = name
        except Exception:
            pass
        return outputs

    def get_output_resolution(self, output_name):
        try:
            res = subprocess.run(["wlr-randr"], capture_output=True, text=True)
            if res.returncode == 0:
                in_output = False
                for line in res.stdout.splitlines():
                    if not line.startswith(" ") and line.strip():
                        if line.split()[0] == output_name:
                            in_output = True
                        else:
                            in_output = False
                    elif in_output and "current" in line:
                        parts = line.strip().split()[0].split("x")
                        if len(parts) == 2:
                            return int(parts[0]), int(parts[1])
        except Exception:
            pass
        return None, None

    def get_output_pos(self, output_name):
        try:
            res = subprocess.run(["wlr-randr"], capture_output=True, text=True)
            if res.returncode == 0:
                in_output = False
                for line in res.stdout.splitlines():
                    if not line.startswith(" ") and line.strip():
                        if line.split()[0] == output_name:
                            in_output = True
                        else:
                            in_output = False
                    elif in_output and "Position:" in line:
                        parts = line.strip().split("Position:")[1].split(",")
                        if len(parts) == 2:
                            return parts[0].strip(), parts[1].strip()
        except Exception:
            pass
        return "0", "0"

    def on_refresh_clicked(self, widget):
        outputs = self.get_outputs()
        self.set_source_id("none")
        self.populate_lists(outputs)
        self.check_current_state()

    def check_current_state(self):
        # 1. Check wl-mirror state
        try:
            res = subprocess.run(["pgrep", "wl-mirror"], capture_output=True, text=True)
            active_wl = []
            if res.returncode == 0:
                for pid in res.stdout.splitlines():
                    pid = pid.strip()
                    if pid:
                        try:
                            with open(f"/proc/{pid}/cmdline", "r") as f:
                                cmd = f.read().split('\0')
                                if len(cmd) >= 2:
                                    active_wl.append(cmd[-2])
                        except Exception:
                            pass
            
            self._is_populating = True
            for out, cb in self.wl_checkboxes.items():
                cb.set_active(out in active_wl)
            self._is_populating = False
            self.update_wl_btn_label()
        except Exception:
            pass

        # 2. Check native mirror state
        try:
            res = subprocess.run(["wlr-randr"], capture_output=True, text=True)
            if res.returncode == 0:
                positions = {}
                current_out = None
                for line in res.stdout.splitlines():
                    if not line.startswith(" ") and line.strip():
                        current_out = line.split()[0]
                    elif "Position:" in line:
                        pos = line.strip().split("Position:")[1].replace(" ", "")
                        if current_out:
                            if pos not in positions:
                                positions[pos] = []
                            positions[pos].append(current_out)

                mirrored_group = None
                for pos, outs in positions.items():
                    if len(outs) >= 2:
                        mirrored_group = outs
                        break

                if mirrored_group:
                    self.mirror_btn.get_style_context().add_class("suggested-action")
                    self.stop_native_btn.set_sensitive(True)

                    source = mirrored_group[0]
                    targets_mirrored = mirrored_group[1:]
                    for out in mirrored_group:
                        if out.startswith("eDP") or out.startswith("LVDS") or out.startswith("DSI"):
                            source = out
                            targets_mirrored = [o for o in mirrored_group if o != out]
                            break
                    
                    outputs = self.get_outputs()
                    display_name = outputs.get(source, source)
                    self.set_source_id(source, display_name)
                            
                    for tgt in targets_mirrored:
                        if tgt in self.target_checkboxes:
                            self._is_populating = True
                            self.target_checkboxes[tgt].set_active(True)
                            self._is_populating = False
                else:
                    self.mirror_btn.get_style_context().remove_class("suggested-action")
                    self.stop_native_btn.set_sensitive(False)
        except Exception:
            pass

    def on_native_mirror_clicked(self, widget):
        source = self.get_source_id()
        targets = self.get_selected_targets()
        if source and source != "none" and targets:
            targets = [t for t in targets if t != source]
            if not targets:
                return
                
            source_w, source_h = self.get_output_resolution(source)
            source_pos_x, source_pos_y = self.get_output_pos(source)
            pos_str = f"{source_pos_x},{source_pos_y}"
            
            saved_positions = self.config.get("saved_positions", {})
            for target in targets:
                target_w, target_h = self.get_output_resolution(target)
                target_pos_x, target_pos_y = self.get_output_pos(target)
                target_pos_str = f"{target_pos_x},{target_pos_y}"
                
                if target_pos_str != pos_str:
                    saved_positions[target] = target_pos_str
                    
                if source_w and target_w:
                    scale = target_w / source_w
                    subprocess.run(["wlr-randr", "--output", target, "--scale", str(scale), "--pos", pos_str])
                else:
                    subprocess.run(["wlr-randr", "--output", target, "--pos", pos_str])
                    
            self.save_config("saved_positions", saved_positions)
            
            self.mirror_btn.get_style_context().add_class("suggested-action")
            self.stop_native_btn.set_sensitive(True)

    def on_stop_native_clicked(self, widget):
        source = self.get_source_id()
        targets = self.get_selected_targets()
        if source and source != "none" and targets:
            targets = [t for t in targets if t != source]
            prev = source
            saved_positions = self.config.get("saved_positions", {})
            for target in targets:
                pos = saved_positions.get(target)
                if pos:
                    subprocess.run(["wlr-randr", "--output", target, "--pos", pos, "--scale", "1"])
                else:
                    subprocess.run(["wlr-randr", "--output", target, "--right-of", prev, "--scale", "1"])
                prev = target
        else:
            try:
                res = subprocess.run(["wlr-randr"], capture_output=True, text=True)
                positions = {}
                current_out = None
                for line in res.stdout.splitlines():
                    if not line.startswith(" ") and line.strip():
                        current_out = line.split()[0]
                    elif "Position:" in line:
                        pos = line.strip().split("Position:")[1].replace(" ", "")
                        if current_out:
                            if pos not in positions:
                                positions[pos] = []
                            positions[pos].append(current_out)
                for pos, outs in positions.items():
                    if len(outs) >= 2:
                        src = outs[0]
                        targets_mirrored = outs[1:]
                        for out in outs:
                            if out.startswith("eDP") or out.startswith("LVDS") or out.startswith("DSI"):
                                src = out
                                targets_mirrored = [o for o in outs if o != out]
                                break
                        prev = src
                        saved_positions = self.config.get("saved_positions", {})
                        for tgt in targets_mirrored:
                            pos = saved_positions.get(tgt)
                            if pos:
                                subprocess.run(["wlr-randr", "--output", tgt, "--pos", pos, "--scale", "1"])
                            else:
                                subprocess.run(["wlr-randr", "--output", tgt, "--right-of", prev, "--scale", "1"])
                            prev = tgt
            except:
                pass
            
        self.mirror_btn.get_style_context().remove_class("suggested-action")
        self.stop_native_btn.set_sensitive(False)
        self._is_populating = True
        for name, cb in self.target_checkboxes.items():
            cb.set_active(False)
        self._is_populating = False
        self.update_target_btn_label()
        self.target_popover.popdown()

if __name__ == "__main__":
    app = WaylandMirrorGUI()
    Gtk.main()
