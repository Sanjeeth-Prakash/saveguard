import tkinter as tk
from tkinter import filedialog, messagebox
import json, os, shutil, ctypes
from pathlib import Path
from datetime import datetime

CONFIG_DIR  = Path(os.getenv("APPDATA", str(Path.home()))) / "SaveGuard"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_CONFIG = {"source": "", "dest": "", "wub": ""}

def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def run_as_admin(exe_path):
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", str(exe_path), None, None, 1)
        if ret <= 32:
            messagebox.showerror("Error", f"Launch failed (code {ret}).\nCheck Wub.exe path in Settings.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def copy_path(src, dst_folder):
    sp, dp = Path(src), Path(dst_folder)
    dp.mkdir(parents=True, exist_ok=True)
    if sp.is_file():
        shutil.copy2(sp, dp / sp.name)
        return sp.name
    else:
        dd = dp / sp.name
        if dd.exists(): shutil.rmtree(dd)
        shutil.copytree(sp, dd)
        return sp.name + "/"


class App(tk.Tk):
    # ── Palette ──────────────────────────────────────────────
    BG       = "#080808"
    SURFACE  = "#0f0f0f"
    CARD     = "#121212"
    BORDER   = "#1e1e1e"
    RED      = "#d62828"
    RED_HOT  = "#ff3c3c"
    RED_DIM  = "#4a0f0f"
    RED_TEXT = "#ff6b6b"
    GOLD     = "#c8922a"
    GOLD_HOT = "#f0b040"
    FG       = "#ececec"
    FG_MID   = "#888888"
    FG_DIM   = "#3a3a3a"

    TITLE_FONT  = ("Consolas", 13, "bold")
    HEAD_FONT   = ("Consolas", 9,  "bold")
    BODY_FONT   = ("Segoe UI", 9)
    SMALL_FONT  = ("Segoe UI", 8)
    TINY_FONT   = ("Segoe UI", 7)
    LABEL_FONT  = ("Consolas", 7,  "bold")

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.settings_open = False
        self._pulse_state = True
        self.title("SaveGuard")
        self.geometry("540x560")
        self.resizable(False, False)
        self.configure(bg=self.BG)
        self._build()
        self._refresh()
        self._pulse()

    # ─────────────────────────── LAYOUT ───────────────────────────
    def _build(self):
        # Top red stripe
        tk.Frame(self, bg=self.RED, height=3).pack(fill="x")

        # ── Header ──
        hdr = tk.Frame(self, bg="#0a0000", height=60)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        lf = tk.Frame(hdr, bg="#0a0000"); lf.pack(side="left", padx=18, pady=10)
        tk.Label(lf, text="⚔", font=("Segoe UI Emoji", 18),
                 bg="#0a0000", fg=self.RED).pack(side="left", padx=(0, 10))
        tc = tk.Frame(lf, bg="#0a0000"); tc.pack(side="left")
        tk.Label(tc, text="SAVEGUARD", font=("Consolas", 14, "bold"),
                 bg="#0a0000", fg=self.FG).pack(anchor="w")
        tk.Label(tc, text="GAME  SAVE  MANAGER", font=("Consolas", 6),
                 bg="#0a0000", fg=self.RED_DIM).pack(anchor="w")

        # Settings gear — top right
        tk.Button(hdr, text="⚙", font=("Segoe UI", 14),
                  bg="#0a0000", fg=self.RED_DIM, relief="flat",
                  activebackground="#0a0000", activeforeground=self.RED,
                  bd=0, cursor="hand2",
                  command=self.open_settings).pack(side="right", padx=18)

        # Separator
        self._sep()

        # ── Path Section ──
        path_frame = tk.Frame(self, bg=self.BG)
        path_frame.pack(fill="x", padx=20, pady=(14, 6))

        self._path_row(path_frame, "SOURCE", "Game save file or folder", "source")
        tk.Frame(path_frame, bg=self.BORDER, height=1).pack(fill="x", pady=6)
        self._path_row(path_frame, "DESTINATION", "Your backup folder", "dest")

        self._sep(margin=20)

        # ── Action Cards ──
        actions = tk.Frame(self, bg=self.BG)
        actions.pack(fill="x", padx=20, pady=(10, 0))

        # SAVE FILE card
        self._action_card(
            actions,
            icon="💾", tag="SAVE FILE",
            desc="Copy save from Source → Destination",
            btn_text="SAVE NOW",
            btn_bg=self.RED, btn_hover=self.RED_HOT,
            command=self.do_save,
            side="left"
        )

        tk.Frame(actions, bg=self.BORDER, width=1).pack(side="left", fill="y", padx=10)

        # TRANSFER BACK card
        self._action_card(
            actions,
            icon="⬆", tag="TRANSFER SAVE",
            desc="Restore save from Destination → Source",
            btn_text="RESTORE NOW",
            btn_bg=self.GOLD, btn_hover=self.GOLD_HOT,
            command=self.do_restore,
            side="left"
        )

        self._sep(margin=20, top=14)

        # ── Ticket Claim ──
        tc_frame = tk.Frame(self, bg=self.BG)
        tc_frame.pack(fill="x", padx=20, pady=(0, 4))
        self._ticket_btn(tc_frame)

        # ── Status bar ──
        self._sep()
        sb = tk.Frame(self, bg="#050505", height=32)
        sb.pack(fill="x", side="bottom"); sb.pack_propagate(False)

        self.dot_lbl = tk.Label(sb, text="●", font=("Consolas", 8),
                                bg="#050505", fg=self.RED)
        self.dot_lbl.pack(side="left", padx=(12, 4), pady=8)

        self.status_var = tk.StringVar(value="READY")
        self.slbl = tk.Label(sb, textvariable=self.status_var,
                             font=("Consolas", 8), bg="#050505", fg=self.FG_MID, anchor="w")
        self.slbl.pack(side="left", pady=8)

        tk.Label(sb, text="created with 💗 by sxnjxxth",
                 font=("Segoe UI", 7, "italic"),
                 bg="#050505", fg="#3a1515").pack(side="right", padx=14)

        self.llbl = tk.Label(sb, text="", font=("Consolas", 7),
                             bg="#050505", fg=self.RED_DIM)
        self.llbl.pack(side="right", padx=(0, 16))

    def _sep(self, margin=0, top=0):
        f = tk.Frame(self, bg=self.BORDER, height=1)
        f.pack(fill="x", padx=margin, pady=(top, 0))

    def _path_row(self, parent, tag, hint, key):
        row = tk.Frame(parent, bg=self.BG); row.pack(fill="x", pady=3)

        # Label column
        lc = tk.Frame(row, bg=self.BG, width=96); lc.pack(side="left"); lc.pack_propagate(False)
        tk.Label(lc, text=tag, font=self.LABEL_FONT,
                 bg=self.BG, fg=self.RED_TEXT).pack(anchor="w")
        tk.Label(lc, text=hint, font=("Segoe UI", 6),
                 bg=self.BG, fg=self.FG_DIM, wraplength=90, justify="left").pack(anchor="w")

        # Entry
        var = tk.StringVar(value=self.cfg.get(key, ""))
        setattr(self, f"var_{key}", var)
        e = tk.Entry(row, textvariable=var, bg=self.CARD, fg=self.FG,
                     insertbackground=self.RED, relief="flat", bd=0,
                     font=self.BODY_FONT,
                     highlightbackground=self.BORDER, highlightthickness=1)
        e.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 6))

        # Buttons
        bc = tk.Frame(row, bg=self.BG); bc.pack(side="right")

        def pick_file(k=key, v=var):
            p = filedialog.askopenfilename(title=f"Pick save file — {k}")
            if p: v.set(p); self.cfg[k] = p; save_config(self.cfg)

        def pick_folder(k=key, v=var):
            p = filedialog.askdirectory(title=f"Pick save folder — {k}")
            if p: v.set(p); self.cfg[k] = p; save_config(self.cfg)

        tk.Button(bc, text="File", font=("Consolas", 7, "bold"),
                  bg=self.RED_DIM, fg=self.FG, relief="flat",
                  activebackground=self.RED, activeforeground="white",
                  bd=0, cursor="hand2", padx=8,
                  command=pick_file).pack(side="left", ipady=5, padx=(0, 3))
        tk.Button(bc, text="Folder", font=("Consolas", 7, "bold"),
                  bg="#1a1a1a", fg=self.FG, relief="flat",
                  activebackground="#2e2e2e", activeforeground="white",
                  bd=0, cursor="hand2", padx=8,
                  command=pick_folder).pack(side="left", ipady=5)

        var.trace_add("write", lambda *_, k=key, v=var: (
            self.cfg.__setitem__(k, v.get()), save_config(self.cfg)))

    def _action_card(self, parent, icon, tag, desc, btn_text, btn_bg, btn_hover, command, side):
        card = tk.Frame(parent, bg=self.CARD,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(side=side, fill="both", expand=True)

        inner = tk.Frame(card, bg=self.CARD); inner.pack(fill="both", padx=14, pady=14)

        top = tk.Frame(inner, bg=self.CARD); top.pack(fill="x", pady=(0, 6))
        tk.Label(top, text=icon, font=("Segoe UI Emoji", 16),
                 bg=self.CARD, fg=btn_bg).pack(side="left", padx=(0, 8))
        tl = tk.Frame(top, bg=self.CARD); tl.pack(side="left")
        tk.Label(tl, text=tag, font=self.LABEL_FONT,
                 bg=self.CARD, fg=self.FG).pack(anchor="w")
        tk.Label(tl, text=desc, font=("Segoe UI", 7),
                 bg=self.CARD, fg=self.FG_MID, wraplength=160, justify="left").pack(anchor="w")

        btn = tk.Button(inner, text=btn_text, font=("Consolas", 9, "bold"),
                        bg=btn_bg, fg="white", relief="flat",
                        activebackground=btn_hover, activeforeground="white",
                        bd=0, cursor="hand2", pady=10, command=command)
        btn.pack(fill="x", pady=(6, 0))

    def _ticket_btn(self, parent):
        wrap = tk.Frame(parent, bg=self.RED_DIM,
                        highlightbackground=self.RED_DIM, highlightthickness=1)
        wrap.pack(fill="x")
        inner = tk.Frame(wrap, bg="#0d0000"); inner.pack(fill="x", padx=1, pady=1)
        row = tk.Frame(inner, bg="#0d0000"); row.pack(fill="x", padx=14, pady=10)
        tk.Label(row, text="🎟", font=("Segoe UI Emoji", 13),
                 bg="#0d0000", fg=self.RED).pack(side="left", padx=(0, 10))
        tl = tk.Frame(row, bg="#0d0000"); tl.pack(side="left", fill="x", expand=True)
        tk.Label(tl, text="TICKET CLAIM", font=self.LABEL_FONT,
                 bg="#0d0000", fg=self.RED_TEXT).pack(anchor="w")
        tk.Label(tl, text="Launch Windows Update Blocker as Administrator",
                 font=("Segoe UI", 7), bg="#0d0000", fg=self.RED_DIM).pack(anchor="w")
        tk.Button(row, text="LAUNCH →", font=("Consolas", 8, "bold"),
                  bg=self.RED, fg="white", relief="flat",
                  activebackground=self.RED_HOT, bd=0, cursor="hand2",
                  padx=14, command=self.do_ticket).pack(side="right", ipady=6)

    # ─────────────────────────── LOGIC ────────────────────────────
    def _refresh(self):
        for k in ("source", "dest", "wub"):
            v = getattr(self, f"var_{k}", None)
            if v: v.set(self.cfg.get(k, ""))

    def _status(self, msg, color=None):
        self.status_var.set(msg.upper())
        self.slbl.config(fg=color or self.FG_MID)

    def _pulse(self):
        self._pulse_state = not self._pulse_state
        self.dot_lbl.config(fg=self.RED if self._pulse_state else self.RED_DIM)
        self.after(900, self._pulse)

    def _check_paths(self):
        if not self.cfg.get("source", "").strip():
            messagebox.showwarning("Missing Source", "Set the source path first."); return False
        if not self.cfg.get("dest", "").strip():
            messagebox.showwarning("Missing Destination", "Set the destination path first."); return False
        return True

    def do_save(self):
        if not self._check_paths(): return
        src, dst = self.cfg["source"].strip(), self.cfg["dest"].strip()
        if not Path(src).exists():
            messagebox.showerror("Not Found", f"Source not found:\n{src}"); return
        try:
            copied = copy_path(src, dst)
            ts = datetime.now().strftime("%H:%M:%S")
            self._status(f"Saved '{copied}' → backup", self.RED_TEXT)
            self.llbl.config(text=f"saved {ts}", fg=self.RED_DIM)
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))
            self._status("Save failed", self.RED_HOT)

    def do_restore(self):
        if not self._check_paths(): return
        src, dst = self.cfg["source"].strip(), self.cfg["dest"].strip()
        sp, dp = Path(src), Path(dst)
        if not dp.exists():
            messagebox.showerror("Not Found", f"Backup folder not found:\n{dst}"); return
        backup_item = dp / sp.name
        if not backup_item.exists():
            messagebox.showerror("Backup Not Found",
                f"No backup of '{sp.name}' in:\n{dst}\n\nRun 'Save Now' first."); return
        try:
            copied = copy_path(str(backup_item), str(sp.parent))
            ts = datetime.now().strftime("%H:%M:%S")
            self._status(f"Restored '{copied}' → game folder", self.GOLD_HOT)
            self.llbl.config(text=f"restored {ts}", fg=self.GOLD)
        except Exception as e:
            messagebox.showerror("Restore Failed", str(e))
            self._status("Restore failed", self.RED_HOT)

    def do_ticket(self):
        wub = self.cfg.get("wub", "").strip()
        if not wub:
            messagebox.showwarning("Not Set",
                "Set the Windows Update Blocker (Wub.exe) path in Settings (⚙) first."); return
        wp = Path(wub)
        if not wp.exists():
            messagebox.showerror("Not Found", f"Wub.exe not found:\n{wub}"); return
        self._status("Launching WUB as admin...", self.RED_TEXT)
        run_as_admin(wp)
        self._status("Ticket Claim launched", self.RED_TEXT)

    def open_settings(self):
        if self.settings_open: return
        self.settings_open = True
        win = tk.Toplevel(self)
        win.title("Settings"); win.geometry("460x180")
        win.resizable(False, False); win.configure(bg=self.BG); win.grab_set()
        tk.Frame(win, bg=self.RED, height=3).pack(fill="x")

        def close(): self.settings_open = False; win.destroy()
        win.protocol("WM_DELETE_WINDOW", close)

        tk.Label(win, text="SETTINGS", font=("Consolas", 11, "bold"),
                 bg=self.BG, fg=self.FG).pack(anchor="w", padx=20, pady=(14, 2))
        tk.Label(win, text="Windows Update Blocker path",
                 font=self.TINY_FONT, bg=self.BG, fg=self.FG_MID).pack(anchor="w", padx=20)
        tk.Frame(win, bg=self.BORDER, height=1).pack(fill="x", padx=20, pady=8)

        body = tk.Frame(win, bg=self.BG); body.pack(fill="x", padx=20)
        tk.Label(body, text="WUB.EXE PATH", font=self.LABEL_FONT,
                 bg=self.BG, fg=self.RED_DIM).pack(anchor="w", pady=(0, 4))
        row = tk.Frame(body, bg=self.BG); row.pack(fill="x")
        v = tk.StringVar(value=self.cfg.get("wub", ""))
        setattr(self, "var_wub", v)
        tk.Entry(row, textvariable=v, bg=self.CARD, fg=self.FG,
                 insertbackground=self.RED, relief="flat", bd=0, font=self.BODY_FONT,
                 highlightbackground=self.BORDER, highlightthickness=1).pack(
            side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        def browse():
            p = filedialog.askopenfilename(title="Select Wub.exe",
                                           filetypes=[("Exe","*.exe"),("All","*.*")])
            if p: v.set(p)
        tk.Button(row, text="Browse", font=("Consolas", 7, "bold"),
                  bg=self.RED, fg="white", relief="flat",
                  activebackground=self.RED_HOT, bd=0, cursor="hand2",
                  padx=10, command=browse).pack(side="right", ipady=6)

        def save_s():
            self.cfg["wub"] = v.get().strip()
            save_config(self.cfg)
            self._status("Settings saved", self.RED_TEXT); close()
        tk.Button(win, text="SAVE", font=("Consolas", 9, "bold"),
                  bg=self.RED, fg="white", relief="flat",
                  activebackground=self.RED_HOT, bd=0, cursor="hand2",
                  pady=10, command=save_s).pack(fill="x", padx=20, pady=14)


if __name__ == "__main__":
    App().mainloop()
