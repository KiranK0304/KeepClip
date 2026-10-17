#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Adw, Gdk, GLib, Pango, Gio

sys.path.insert(0, os.path.expanduser("~/.local/share/clipboard-history"))
import store
import uinput_paste

def format_time(ts):
    diff = max(0, int(time.time() - ts))
    if diff < 10:
        return "Just now"
    elif diff < 60:
        return f"{diff}s ago"
    elif diff < 3600:
        return f"{diff // 60}m ago"
    elif diff < 86400:
        return f"{diff // 3600}h ago"
    else:
        return time.strftime("%b %d, %I:%M %p", time.localtime(ts))

class ClipboardRow(Gtk.ListBoxRow):
    def __init__(self, item, on_select, on_pin, on_delete):
        super().__init__()
        self.item = item
        self.on_select = on_select

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        # Content container
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content_box.set_hexpand(True)

        # Text snippet preview
        preview_text = item["text"]
        lines = preview_text.splitlines()
        if len(lines) > 3:
            preview_display = "\n".join(lines[:3]) + "..."
        else:
            preview_display = preview_text

        text_label = Gtk.Label(label=preview_display)
        text_label.set_wrap(True)
        text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_lines(3)
        text_label.set_ellipsize(Pango.EllipsizeMode.END)
        text_label.set_xalign(0.0)
        text_label.add_css_class("clipboard-text")
        content_box.append(text_label)

        # Meta label (timestamp & length)
        char_count = len(item["text"])
        meta_str = f"{format_time(item['timestamp'])} • {char_count} chars"
        if item.get("pinned"):
            meta_str = f"📌 Pinned • {meta_str}"

        meta_label = Gtk.Label(label=meta_str)
        meta_label.set_xalign(0.0)
        meta_label.add_css_class("dim-label")
        meta_label.add_css_class("caption")
        content_box.append(meta_label)

        box.append(content_box)

        # Actions box
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        btn_box.set_valign(Gtk.Align.CENTER)

        # Pin button
        pin_icon = "starred-symbolic" if item.get("pinned") else "non-starred-symbolic"
        pin_btn = Gtk.Button.new_from_icon_name(pin_icon)
        pin_btn.add_css_class("flat")
        pin_btn.add_css_class("circular")
        pin_btn.set_tooltip_text("Unpin" if item.get("pinned") else "Pin to top")
        pin_btn.connect("clicked", lambda b: on_pin(item["id"]))
        btn_box.append(pin_btn)

        # Delete button
        del_btn = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        del_btn.add_css_class("flat")
        del_btn.add_css_class("circular")
        del_btn.set_tooltip_text("Delete snippet")
        del_btn.connect("clicked", lambda b: on_delete(item["id"]))
        btn_box.append(del_btn)

        box.append(btn_box)
        self.set_child(box)

class ClipboardAppWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Clipboard History")
        self.set_default_size(430, 540)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header bar
        header = Adw.HeaderBar()
        title_widget = Adw.WindowTitle(title="Clipboard History", subtitle="Press Win + V anytime")
        header.set_title_widget(title_widget)

        clear_btn = Gtk.Button(label="Clear")
        clear_btn.add_css_class("flat")
        clear_btn.set_tooltip_text("Clear all non-pinned history")
        clear_btn.connect("clicked", self.on_clear_clicked)
        header.pack_start(clear_btn)

        main_box.append(header)

        # Search Bar
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)
        search_box.set_margin_top(8)
        search_box.set_margin_bottom(8)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search copied items... (Esc to close)")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("activate", self.on_search_activate)
        search_box.append(self.search_entry)
        main_box.append(search_box)

        # Scrolled List
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.add_css_class("boxed-list")
        self.listbox.set_margin_start(12)
        self.listbox.set_margin_end(12)
        self.listbox.set_margin_bottom(12)
        self.listbox.connect("row-activated", self.on_row_activated)

        scrolled.set_child(self.listbox)
        main_box.append(scrolled)

        # Bottom hint bar
        hint_label = Gtk.Label(label="Enter to paste directly • Esc to close • ↑↓ to navigate")
        hint_label.add_css_class("dim-label")
        hint_label.add_css_class("caption")
        hint_label.set_margin_bottom(6)
        main_box.append(hint_label)

        self.set_content(main_box)

        # Key controller
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_ctrl)

        self.paster = uinput_paste.VirtualPaster()
        self.sync_active_clipboard()
        self.load_items()

        # Load custom CSS
        self.apply_css()

    def apply_css(self):
        css = """
        .clipboard-text {
            font-family: monospace, sans-serif;
            font-size: 13px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def sync_active_clipboard(self):
        try:
            res = subprocess.run(
                ["wl-paste", "-n"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=0.4
            )
            if res.returncode == 0:
                raw = res.stdout
                if b"\x00" not in raw:
                    text = raw.decode("utf-8", errors="ignore").strip()
                    if text:
                        store.add_entry(text)
        except Exception:
            pass

    def load_items(self, query=""):
        # Clear existing rows
        while True:
            row = self.listbox.get_row_at_index(0)
            if row is None:
                break
            self.listbox.remove(row)

        items = store.get_all_entries(query)
        if not items:
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            empty_box.set_margin_top(40)
            empty_box.set_margin_bottom(40)
            empty_lbl = Gtk.Label(label="No clipboard items found")
            empty_lbl.add_css_class("dim-label")
            empty_box.append(empty_lbl)
            self.listbox.append(empty_box)
            return

        for item in items:
            row = ClipboardRow(
                item=item,
                on_select=self.select_and_paste,
                on_pin=self.handle_pin,
                on_delete=self.handle_delete
            )
            self.listbox.append(row)

        first_row = self.listbox.get_row_at_index(0)
        if first_row:
            self.listbox.select_row(first_row)

    def on_search_changed(self, entry):
        self.load_items(entry.get_text())

    def on_search_activate(self, entry):
        selected_row = self.listbox.get_selected_row()
        if selected_row and hasattr(selected_row, "item"):
            self.select_and_paste(selected_row.item["text"])

    def on_row_activated(self, listbox, row):
        if hasattr(row, "item"):
            self.select_and_paste(row.item["text"])

    def select_and_paste(self, text):
        try:
            p1 = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
            p1.communicate(input=text.encode("utf-8"))
            p2 = subprocess.Popen(["wl-copy", "--primary"], stdin=subprocess.PIPE)
            p2.communicate(input=text.encode("utf-8"))
        except Exception:
            pass
        self.close()
        if self.paster and self.paster.fd is not None:
            GLib.timeout_add(100, lambda: self.paster.paste() and False)

    def handle_pin(self, item_id):
        store.toggle_pin(item_id)
        self.load_items(self.search_entry.get_text())

    def handle_delete(self, item_id):
        store.delete_entry(item_id)
        self.load_items(self.search_entry.get_text())

    def on_clear_clicked(self, btn):
        store.clear_history()
        self.load_items(self.search_entry.get_text())

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.close()
            return True
        elif keyval in (Gdk.KEY_Down, Gdk.KEY_Up):
            # Let ListBox handle navigation
            current_selected = self.listbox.get_selected_row()
            if current_selected:
                idx = current_selected.get_index()
                if keyval == Gdk.KEY_Down:
                    next_row = self.listbox.get_row_at_index(idx + 1)
                    if next_row:
                        self.listbox.select_row(next_row)
                else:
                    prev_row = self.listbox.get_row_at_index(idx - 1)
                    if prev_row:
                        self.listbox.select_row(prev_row)
                return True
        elif keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            selected_row = self.listbox.get_selected_row()
            if selected_row and hasattr(selected_row, "item"):
                self.select_and_paste(selected_row.item["text"])
                return True
        return False

def main():
    app = Adw.Application(flags=Gio.ApplicationFlags.NON_UNIQUE)

    def on_activate(app):
        win = ClipboardAppWindow(app)
        win.present()

    app.connect("activate", on_activate)
    app.run([])

if __name__ == "__main__":
    main()
