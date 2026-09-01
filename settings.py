import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from tavern_shared.paths import _tavern_data_dir
from tavern_shared.theme import AMBER, AMBERDIM, BG, BORDER, MUTED, PARCH, SURF, SURF2


SETTINGS_FILE = Path(_tavern_data_dir()) / "town_cleanup_settings.json"

DEFAULT_SETTINGS = {
    "cleanup_delay": 300,
    "tree_cleanup": True,
    "cave_cleanup": True,
    "redwood_box": True,
    "spriggull_cleanup": True,
    "lag_items_cleanup": True,
    "custom_cleanup": False,
    "custom_cleanup_items": [],
}


def load_settings():
    try:
        if not SETTINGS_FILE.exists():
            return dict(DEFAULT_SETTINGS)

        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    try:
        with SETTINGS_FILE.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, sort_keys=True)
        return True
    except Exception:
        return False


def get_setting(key, default=None):
    settings = load_settings()
    return settings.get(key, default)


def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


class TownCleanupSettingsWindow:
    def __init__(self, master=None):
        self.settings = load_settings()
        self.window = master if master is not None else self._create_root_window()
        self._build_ui()

    def _create_root_window(self):
        try:
            root = getattr(tk, "_default_root", None)
            if root is not None and root.winfo_exists():
                return tk.Toplevel(root)
        except Exception:
            pass

        win = tk.Tk()
        win.withdraw()
        return win

    def _build_ui(self):
        win = self.window
        win.title("Town Cleanup Settings")
        win.geometry("500x560")
        win.resizable(False, False)
        win.configure(bg=BG)

        style = ttk.Style(win)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            ".",
            background=BG,
            foreground=PARCH,
            fieldbackground=SURF,
            borderwidth=0,
            selectbackground=AMBERDIM,
            selectforeground="#ffd080",
        )
        style.configure("Tav.Card.TFrame", background=SURF)
        style.configure("Tav.Section.TLabelframe", background=SURF, foreground=PARCH)
        style.configure("Tav.Section.TLabelframe.Label", background=SURF, foreground=AMBER, font=("Georgia", 9, "bold"))
        style.configure("Tav.Heading.TLabel", background=BG, foreground=AMBER, font=("Georgia", 15, "bold"))
        style.configure("Tav.Body.TLabel", background=BG, foreground=PARCH, font=("Segoe UI", 9))
        style.configure("Tav.Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Tav.Checkbutton", background=SURF, foreground=PARCH)
        style.map("Tav.Checkbutton", background=[("active", SURF2)], foreground=[("active", PARCH)])
        style.configure("Tav.TSpinbox", fieldbackground=SURF2, background=SURF2, foreground=PARCH, arrowcolor=AMBERDIM)
        style.map("Tav.TSpinbox", fieldbackground=[("readonly", SURF2)], foreground=[("readonly", PARCH)])
        style.configure("Tav.Accent.TButton", background="#3d2a0a", foreground=AMBER, borderwidth=0, padding=(14, 7))
        style.map(
            "Tav.Accent.TButton",
            background=[("active", "#5a3d0e"), ("pressed", "#4a320d")],
            foreground=[("active", "#ffd080"), ("pressed", "#ffd080")],
        )
        style.configure("Tav.Secondary.TButton", background=SURF2, foreground=PARCH, borderwidth=0, padding=(12, 7))
        style.map(
            "Tav.Secondary.TButton",
            background=[("active", "#392d22"), ("pressed", "#2d2420")],
            foreground=[("active", PARCH), ("pressed", PARCH)],
        )

        container = ttk.Frame(win, padding=18, style="Tav.Card.TFrame")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Town Cleanup", style="Tav.Heading.TLabel").pack(anchor="w", pady=(0, 12))

        delay_frame = ttk.Frame(container, style="Tav.Card.TFrame")
        delay_frame.pack(fill="x", pady=(0, 12))
        ttk.Label(delay_frame, text="Delay between cleanups (seconds):", style="Tav.Body.TLabel").pack(anchor="w")

        self.delay_var = tk.IntVar(value=int(self.settings.get("cleanup_delay", DEFAULT_SETTINGS["cleanup_delay"])))
        delay_entry = ttk.Spinbox(
            delay_frame,
            from_=10,
            to=3600,
            increment=10,
            textvariable=self.delay_var,
            width=12,
            style="Tav.TSpinbox",
        )
        delay_entry.pack(anchor="w", pady=(6, 0))

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(0, 12))

        toggles_frame = tk.LabelFrame(
            container,
            text="Cleanup Types",
            bg=SURF,
            fg=PARCH,
            bd=1,
            padx=10,
            pady=8,
            relief="groove",
            font=("Georgia", 9, "bold"),
        )
        toggles_frame.pack(fill="x", pady=(0, 14))

        self.tree_var = tk.BooleanVar(value=bool(self.settings.get("tree_cleanup", DEFAULT_SETTINGS["tree_cleanup"])))
        self.cave_var = tk.BooleanVar(value=bool(self.settings.get("cave_cleanup", DEFAULT_SETTINGS["cave_cleanup"])))
        self.redwood_var = tk.BooleanVar(value=bool(self.settings.get("redwood_box", DEFAULT_SETTINGS["redwood_box"])))
        self.spriggull_var = tk.BooleanVar(value=bool(self.settings.get("spriggull_cleanup", DEFAULT_SETTINGS["spriggull_cleanup"])))
        self.lag_items_var = tk.BooleanVar(value=bool(self.settings.get("lag_items_cleanup", DEFAULT_SETTINGS["lag_items_cleanup"])))
        self.custom_var = tk.BooleanVar(value=bool(self.settings.get("custom_cleanup", DEFAULT_SETTINGS["custom_cleanup"])))
        self.custom_items_var = tk.StringVar(value=",".join(self.settings.get("custom_cleanup_items", DEFAULT_SETTINGS["custom_cleanup_items"])))

        checks = [
            ("Tree Cleanup", self.tree_var),
            ("Cave Cleanup", self.cave_var),
            ("Redwood Box", self.redwood_var),
            ("Spriggull Cleanup", self.spriggull_var),
            ("Lag Items (rusty tools, arrows, bones, etc.)", self.lag_items_var),
            ("Custom Cleanup", self.custom_var),
        ]
         ## Add a text entry for custom cleanup items
        custom_items_frame = ttk.Frame(toggles_frame, style="Tav.Card.TFrame")
        custom_items_frame.pack(fill="x", pady=(6, 0))

        tk.Label(custom_items_frame, text="Custom Items (comma-separated item names) (e.g., item1, item2, item3):", bg=SURF, fg=PARCH).pack(anchor="w", pady=(0, 2))
        tk.Entry(custom_items_frame, textvariable=self.custom_items_var).pack(fill="x", pady=(0, 2))

        for label, variable in checks:
            tk.Checkbutton(
                toggles_frame,
                text=label,
                variable=variable,
                bg=SURF,
                fg=PARCH,
                activebackground=SURF,
                activeforeground=PARCH,
                selectcolor=SURF2,
                highlightthickness=0,
                anchor="w",
            ).pack(anchor="w", pady=2)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=(0, 12))

        actions = ttk.Frame(container, style="Tav.Card.TFrame")
        actions.pack(fill="x")

        ttk.Button(actions, text="Save", command=self._save_settings, style="Tav.Accent.TButton").pack(side="right", padx=(6, 0))
        ttk.Button(actions, text="Reset Defaults", command=self._reset_defaults, style="Tav.Secondary.TButton").pack(side="right")

        if hasattr(win, "transient"):
            try:
                win.transient()
            except Exception:
                pass
        try:
            win.grab_set()
        except Exception:
            pass

    def _save_settings(self):
        new_settings = {
            "cleanup_delay": max(10, int(self.delay_var.get())),
            "tree_cleanup": bool(self.tree_var.get()),
            "cave_cleanup": bool(self.cave_var.get()),
            "redwood_box": bool(self.redwood_var.get()),
            "spriggull_cleanup": bool(self.spriggull_var.get()),
            "lag_items_cleanup": bool(self.lag_items_var.get()),
            "custom_cleanup": bool(self.custom_var.get()),
            "custom_cleanup_items": [item.strip() for item in self.custom_items_var.get().split(",") if item.strip()],
        }
        self.settings = new_settings
        ok = save_settings(new_settings)
        if ok:
            try:
                self.window.title("Town Cleanup Settings - Saved")
            except Exception:
                pass
        else:
            try:
                self.window.title("Town Cleanup Settings - Save Failed")
            except Exception:
                pass

    def _reset_defaults(self):
        self.delay_var.set(DEFAULT_SETTINGS["cleanup_delay"])
        self.tree_var.set(DEFAULT_SETTINGS["tree_cleanup"])
        self.cave_var.set(DEFAULT_SETTINGS["cave_cleanup"])
        self.redwood_var.set(DEFAULT_SETTINGS["redwood_box"])
        self.spriggull_var.set(DEFAULT_SETTINGS["spriggull_cleanup"])
        self.lag_items_var.set(DEFAULT_SETTINGS["lag_items_cleanup"])
        self.custom_var.set(DEFAULT_SETTINGS["custom_cleanup"])
        self.custom_items_var.set(",".join(DEFAULT_SETTINGS["custom_cleanup_items"]))
        self._save_settings()


def _open_town_cleanup_window():
    try:
        TownCleanupSettingsWindow()
    except Exception as exc:
        print(f"[Town Cleanup] Failed to open settings window: {exc}")


def register_town_cleanup_settings_window():
    try:
        from server.core.header_registry import register_header_button

        register_header_button(
            key="town_cleanup",
            icon_text="🧹 Town Cleanup",
            command_attr="_open_town_cleanup_window",
            label="Town Cleanup",
        )

        from server.core.launcher_window import ServerLauncher

        ServerLauncher._open_town_cleanup_window = lambda _self: _open_town_cleanup_window()  # type: ignore
    except Exception as e:
        print(f"[Town Cleanup] Failed to register header button: {e}")