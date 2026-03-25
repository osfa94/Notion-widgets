import tkinter as tk
from tkinter import font as tkfont
import time


BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
SURFACE = "#313244"
BTN_FG = "#1e1e2e"


class TimerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Timer")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._mode = tk.StringVar(value="countdown")
        self._running = False
        self._start_time = 0
        self._remaining = 0
        self._after_id = None

        self._build_ui()

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        pad = {"padx": 20, "pady": 10}

        # Mode tabs
        tab_frame = tk.Frame(self, bg=BG)
        tab_frame.pack(fill="x", **pad)

        for text, value in [("Countdown", "countdown"), ("Stoppuhr", "stopwatch")]:
            tk.Radiobutton(
                tab_frame, text=text, variable=self._mode, value=value,
                command=self._on_mode_change,
                bg=BG, fg=FG, selectcolor=SURFACE,
                activebackground=BG, activeforeground=ACCENT,
                font=("Segoe UI", 11), indicatoron=False,
                relief="flat", padx=14, pady=6,
                bd=0, cursor="hand2",
            ).pack(side="left", padx=(0, 6))

        # Time display
        disp_frame = tk.Frame(self, bg=SURFACE, bd=0)
        disp_frame.pack(fill="x", padx=20, pady=(0, 10))

        big_font = tkfont.Font(family="Courier New", size=64, weight="bold")
        self._time_label = tk.Label(
            disp_frame, text="00:00:00", font=big_font,
            bg=SURFACE, fg=ACCENT, pady=20, padx=30,
        )
        self._time_label.pack()

        self._status_label = tk.Label(
            disp_frame, text="", font=("Segoe UI", 11),
            bg=SURFACE, fg=YELLOW,
        )
        self._status_label.pack(pady=(0, 10))

        # Input (countdown only)
        self._input_frame = tk.Frame(self, bg=BG)
        self._input_frame.pack(fill="x", **pad)

        tk.Label(self._input_frame, text="Dauer (HH:MM:SS oder Sekunden):",
                 bg=BG, fg=FG, font=("Segoe UI", 10)).pack(anchor="w")

        entry_frame = tk.Frame(self._input_frame, bg=SURFACE, bd=0)
        entry_frame.pack(fill="x", pady=(4, 0))

        self._duration_var = tk.StringVar(value="00:05:00")
        self._entry = tk.Entry(
            entry_frame, textvariable=self._duration_var,
            font=("Courier New", 16), bg=SURFACE, fg=FG,
            insertbackground=FG, relief="flat", bd=8,
        )
        self._entry.pack(fill="x")

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", **pad)

        self._start_btn = self._make_btn(btn_frame, "▶  Start", GREEN, self._start)
        self._start_btn.pack(side="left", padx=(0, 8))

        self._pause_btn = self._make_btn(btn_frame, "⏸  Pause", YELLOW, self._pause)
        self._pause_btn.pack(side="left", padx=(0, 8))
        self._pause_btn.config(state="disabled")

        self._reset_btn = self._make_btn(btn_frame, "↺  Reset", RED, self._reset)
        self._reset_btn.pack(side="left")

    def _make_btn(self, parent, text, color, cmd):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=color, fg=BTN_FG, activebackground=color,
            font=("Segoe UI", 11, "bold"), relief="flat",
            padx=16, pady=8, cursor="hand2", bd=0,
        )

    # --------------------------------------------------------- mode switch --

    def _on_mode_change(self):
        self._reset()
        if self._mode.get() == "stopwatch":
            self._input_frame.pack_forget()
            self._time_label.config(fg=GREEN)
        else:
            self._input_frame.pack(fill="x", padx=20, pady=10,
                                   before=self.nametowidget(
                                       self.pack_slaves()[-1].winfo_name()))
            self._time_label.config(fg=ACCENT)

    # ------------------------------------------------------------ actions --

    def _start(self):
        if self._running:
            return
        if self._mode.get() == "countdown":
            if self._remaining == 0:
                self._remaining = self._parse_duration()
                if self._remaining is None:
                    return
            self._running = True
            self._tick_countdown()
        else:
            self._start_time = time.time() - self._remaining
            self._running = True
            self._tick_stopwatch()

        self._start_btn.config(state="disabled")
        self._pause_btn.config(state="normal")
        self._status_label.config(text="läuft…", fg=GREEN)

    def _pause(self):
        if not self._running:
            return
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
        self._start_btn.config(state="normal")
        self._pause_btn.config(state="disabled")
        self._status_label.config(text="pausiert", fg=YELLOW)

    def _reset(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
        self._remaining = 0
        self._time_label.config(text="00:00:00")
        self._start_btn.config(state="normal")
        self._pause_btn.config(state="disabled")
        self._status_label.config(text="")

    # ------------------------------------------------------------- ticks --

    def _tick_countdown(self):
        if not self._running:
            return
        self._time_label.config(text=self._fmt(self._remaining))
        if self._remaining <= 0:
            self._running = False
            self._time_label.config(text="00:00:00", fg=RED)
            self._status_label.config(text="Zeit abgelaufen! ⏰", fg=RED)
            self._start_btn.config(state="normal")
            self._pause_btn.config(state="disabled")
            self._flash(6)
            return
        self._remaining -= 1
        self._after_id = self.after(1000, self._tick_countdown)

    def _tick_stopwatch(self):
        if not self._running:
            return
        elapsed = int(time.time() - self._start_time)
        self._remaining = elapsed
        self._time_label.config(text=self._fmt(elapsed))
        self._after_id = self.after(100, self._tick_stopwatch)

    def _flash(self, n):
        if n <= 0:
            self._time_label.config(fg=RED)
            return
        color = RED if n % 2 == 0 else BG
        self._time_label.config(fg=color)
        self.after(400, lambda: self._flash(n - 1))

    # ---------------------------------------------------------------- util --

    def _parse_duration(self):
        raw = self._duration_var.get().strip()
        try:
            if ":" in raw:
                parts = list(map(int, raw.split(":")))
                if len(parts) == 2:
                    return parts[0] * 60 + parts[1]
                elif len(parts) == 3:
                    return parts[0] * 3600 + parts[1] * 60 + parts[2]
            return int(raw)
        except ValueError:
            self._status_label.config(text="Ungültige Eingabe!", fg=RED)
            return None

    @staticmethod
    def _fmt(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    app = TimerApp()
    app.mainloop()

