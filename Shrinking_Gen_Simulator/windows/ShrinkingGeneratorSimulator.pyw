"""
Shrinking Generator Interactive Simulator
Author-ready educational GUI for a VHDL-based 31-bit/32-bit LFSR shrinking generator.

The simulator follows the uploaded VHDL behavior exactly:
- LFSR31 output bit: r(0)
- LFSR31 feedback: r(0) xor r(3)
- LFSR31 next state: feedback & r(30 downto 1)
- LFSR32 output bit: r(0)
- LFSR32 feedback: r(0) xor r(1) xor r(2) xor r(22)
- LFSR32 next state: feedback & r(31 downto 1)
- Shrinking rule: if selector bit is 1, data bit is accepted; otherwise it is discarded.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass
from typing import List, Tuple, Optional


APP_TITLE = "Shrinking Generator Interactive Simulator v4"


@dataclass
class StepResult:
    cycle: int
    sel_before: int
    dat_before: int
    sel_bit: int
    dat_bit: int
    sel_feedback: int
    dat_feedback: int
    sel_after: int
    dat_after: int
    accepted: bool
    output_bit: int


class LFSR:
    def __init__(self, width: int, taps: List[int], seed: Optional[int] = None):
        self.width = width
        self.taps = list(taps)
        self.mask = (1 << width) - 1
        self.default_seed = self.mask
        self.state = self.default_seed if seed is None else self._sanitize_seed(seed)

    def _sanitize_seed(self, seed: int) -> int:
        seed = int(seed) & self.mask
        if seed == 0:
            return self.default_seed
        return seed

    def load(self, seed: int) -> bool:
        """Load seed. Returns True if all-zero seed was replaced with all ones."""
        seed = int(seed) & self.mask
        replaced = seed == 0
        self.state = self.default_seed if replaced else seed
        return replaced

    def output_bit(self) -> int:
        return self.state & 1

    def feedback_bit(self) -> int:
        feedback = 0
        for tap in self.taps:
            feedback ^= (self.state >> tap) & 1
        return feedback

    def step(self) -> Tuple[int, int, int, int]:
        """Return before, output, feedback, after."""
        before = self.state
        out = self.output_bit()
        feedback = self.feedback_bit()
        self.state = ((feedback << (self.width - 1)) | (self.state >> 1)) & self.mask
        after = self.state
        return before, out, feedback, after

    def bit_string(self) -> str:
        return format(self.state, "0{}b".format(self.width))

    def hex_string(self) -> str:
        width_hex = (self.width + 3) // 4
        return "0x" + format(self.state, "0{}X".format(width_hex))


def parse_seed(text: str, width: int) -> int:
    s = (text or "").strip().replace("_", "").replace(" ", "")
    if not s:
        raise ValueError("Seed cannot be empty.")
    if s.lower().startswith("0b"):
        value = int(s[2:], 2)
    elif s.lower().startswith("0x"):
        value = int(s[2:], 16)
    else:
        # Pure binary strings are accepted when they only contain 0/1 and are longer than one bit.
        if all(ch in "01" for ch in s) and len(s) > 1:
            value = int(s, 2)
        else:
            value = int(s, 10)
    if value < 0:
        raise ValueError("Seed must be non-negative.")
    mask = (1 << width) - 1
    return value & mask


class RegisterCanvas(tk.Canvas):
    def __init__(self, master, title: str, width_bits: int, taps: List[int], **kwargs):
        super().__init__(master, height=115, background="white", highlightthickness=1, highlightbackground="#c7c7c7", **kwargs)
        self.title = title
        self.width_bits = width_bits
        self.taps = set(taps)
        self.current_state = 0
        self.last_feedback = 0
        self.bind("<Configure>", lambda _event: self.draw(self.current_state, self.last_feedback))

    def draw(self, state: int, feedback: int = 0):
        self.current_state = state
        self.last_feedback = feedback
        self.delete("all")
        w = max(self.winfo_width(), 900)
        h = max(self.winfo_height(), 115)
        margin_x = 18
        top = 38
        box_h = 30
        usable_w = w - 2 * margin_x
        box_w = max(17, min(31, usable_w / self.width_bits))
        start_x = (w - box_w * self.width_bits) / 2

        self.create_text(14, 14, text=self.title, anchor="w", font=("Segoe UI", 10, "bold"), fill="#0b1f5f")
        self.create_text(w - 14, 14, text="MSB on left, LSB/output bit on right", anchor="e", font=("Segoe UI", 8), fill="#555")

        for pos in range(self.width_bits):
            bit_index = self.width_bits - 1 - pos  # Display MSB -> LSB
            bit = (state >> bit_index) & 1
            x0 = start_x + pos * box_w
            y0 = top
            x1 = x0 + box_w
            y1 = y0 + box_h

            fill = "#f6f8fb"
            outline = "#2d2d2d"
            text_fill = "#111"
            if bit_index in self.taps:
                fill = "#fff0c2"  # feedback tap
            if bit_index == 0:
                fill = "#d8f5dc"  # output bit
            if bit_index in self.taps and bit_index == 0:
                fill = "#c9edff"

            self.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=1)
            self.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(bit), font=("Consolas", 12, "bold"), fill=text_fill)

            # Show only useful labels to keep it readable.
            if bit_index in self.taps or bit_index in (self.width_bits - 1, 0):
                self.create_text((x0 + x1) / 2, y1 + 13, text="b{}".format(bit_index), font=("Segoe UI", 7), fill="#333")

        tap_expr = " ⊕ ".join("bit{}".format(t) for t in self.taps)
        self.create_text(start_x, h - 18, text="feedback = {} = {}".format(tap_expr, feedback), anchor="w", font=("Segoe UI", 9, "bold"), fill="#8a4b00")
        self.create_text(w - 16, h - 18, text="green: output bit  |  yellow: XOR taps", anchor="e", font=("Segoe UI", 8), fill="#444")


class FlowAnimationCanvas(tk.Canvas):
    """Shows the XOR feedback calculation and shrinking decision as an animated flow."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("width", 350)
        kwargs.setdefault("height", 405)
        kwargs.setdefault("background", "white")
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", "#c7c7c7")
        super().__init__(master, **kwargs)
        self._jobs = []
        self._last_result: Optional[StepResult] = None
        self._pool_size = 0
        self.bind("<Configure>", lambda _event: self.draw_idle())

    def cancel_jobs(self):
        for job in self._jobs:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self._jobs.clear()

    def _bit(self, state: int, idx: int) -> int:
        return (state >> idx) & 1

    def draw_idle(self, message: str = "Press Step Clock to watch XOR and shrinking flow."):
        self.cancel_jobs()
        self.delete("all")
        w = max(self.winfo_width(), 330)
        self.create_text(12, 12, text="Live XOR / Flow Explanation", anchor="w", font=("Segoe UI", 10, "bold"), fill="#0b1f5f")
        self.create_rectangle(18, 42, w - 18, 105, fill="#f6f8fb", outline="#9db9d4")
        self.create_text(w / 2, 72, text=message, anchor="center", font=("Segoe UI", 9), fill="#333", width=w - 60)
        self.create_text(w / 2, 140, text="This panel animates:", anchor="center", font=("Segoe UI", 9, "bold"), fill="#111")
        lines = [
            "1) XOR feedback bits are calculated",
            "2) feedback is inserted into MSB",
            "3) selector decides accept/discard",
            "4) accepted data bit goes to output pool",
        ]
        for i, line in enumerate(lines):
            self.create_text(35, 168 + i * 23, text=line, anchor="w", font=("Segoe UI", 8), fill="#444")

    def animate(self, result: StepResult, pool_bits: List[str]):
        self.cancel_jobs()
        self._last_result = result
        self._pool_size = len(pool_bits)
        pool_snapshot = list(pool_bits)
        stages = list(range(8))
        delay = 0
        for stage in stages:
            job = self.after(delay, lambda s=stage: self._draw_stage(result, pool_snapshot, s))
            self._jobs.append(job)
            delay += 260

    def _draw_box(self, x0, y0, x1, y1, text, fill="#f6f8fb", outline="#1f4e79", font_size=8, bold=False):
        self.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=2)
        weight = "bold" if bold else "normal"
        self.create_text((x0+x1)/2, (y0+y1)/2, text=text, font=("Segoe UI", font_size, weight), fill="#111", width=max(10, x1-x0-8))

    def _arrow(self, x0, y0, x1, y1, fill="#1f4e79", width=2):
        self.create_line(x0, y0, x1, y1, fill=fill, width=width, arrow="last", arrowshape=(10, 12, 4))

    def _token(self, x, y, text, fill="#ffcc66"):
        self.create_oval(x-11, y-11, x+11, y+11, fill=fill, outline="#333", width=1)
        self.create_text(x, y, text=text, font=("Segoe UI", 8, "bold"), fill="#111")

    def _pool_preview(self, pool_bits):
        raw = "".join(pool_bits)
        if not raw:
            return "empty"
        tail = raw[-40:]
        grouped = " ".join(tail[i:i+8] for i in range(0, len(tail), 8))
        return grouped

    def _draw_pool_preview(self, y, pool_bits, highlight_last=False):
        w = max(self.winfo_width(), 330)
        raw_len = len(pool_bits)
        preview = self._pool_preview(pool_bits)
        fill = "#effaf1" if highlight_last else "#fbfbfb"
        self.create_rectangle(18, y, w-18, y+54, fill=fill, outline="#2f6b3f", width=2)
        self.create_text(26, y+12, text="Output Pool Preview  |  size = {}".format(raw_len), anchor="w", font=("Segoe UI", 8, "bold"), fill="#1f5f30")
        self.create_text(26, y+35, text=preview, anchor="w", font=("Consolas", 9, "bold"), fill="#111", width=w-52)

    def _draw_stage(self, r: StepResult, pool_bits: List[str], stage: int):
        self.delete("all")
        w = max(self.winfo_width(), 330)
        pool_size = len(pool_bits)
        self.create_text(12, 12, text="Cycle {}: feedback calculation and shrinking decision".format(r.cycle), anchor="w", font=("Segoe UI", 9, "bold"), fill="#0b1f5f")
        self.create_text(12, 28, text="Note: feedback bits update the next state; shrinking decision uses current r31(0) and r32(0).", anchor="w", font=("Segoe UI", 7), fill="#555")

        # Selector feedback row
        s_b0 = self._bit(r.sel_before, 0)
        s_b3 = self._bit(r.sel_before, 3)
        self.create_text(16, 42, text="31-bit selector feedback (next MSB)", anchor="w", font=("Segoe UI", 8, "bold"), fill="#333")
        self._draw_box(18, 58, 73, 88, "b0\n{}".format(s_b0), fill="#d8f5dc")
        self._draw_box(88, 58, 143, 88, "b3\n{}".format(s_b3), fill="#fff0c2")
        self._draw_box(176, 55, 226, 91, "⊕", fill="#eaf2f8", font_size=16, bold=True)
        self._draw_box(260, 58, w-18, 88, "NEXT FB={} → MSB".format(r.sel_feedback), fill="#f7fbf7" if stage >= 2 else "#f6f8fb")
        self._arrow(73, 73, 176, 73)
        self._arrow(143, 73, 176, 73)
        self._arrow(226, 73, 260, 73)
        if stage == 1:
            self._token(124, 73, str(s_b0), "#d8f5dc")
            self._token(152, 73, str(s_b3), "#fff0c2")
        elif stage >= 2:
            self._token(245, 73, str(r.sel_feedback), "#bfe8c5")

        # Data feedback row
        d_vals = [self._bit(r.dat_before, i) for i in (0, 1, 2, 22)]
        self.create_text(16, 112, text="32-bit data feedback (next MSB)", anchor="w", font=("Segoe UI", 8, "bold"), fill="#333")
        x = 18
        labels = ["b0", "b1", "b2", "b22"]
        for label, val in zip(labels, d_vals):
            fill = "#d8f5dc" if label == "b0" else "#fff0c2"
            self._draw_box(x, 128, x+43, 158, "{}\n{}".format(label, val), fill=fill, font_size=7)
            self._arrow(x+43, 143, 206, 143)
            x += 48
        self._draw_box(206, 125, 252, 161, "⊕", fill="#eaf2f8", font_size=16, bold=True)
        self._draw_box(280, 128, w-18, 158, "NEXT FB={} → MSB".format(r.dat_feedback), fill="#f7fbf7" if stage >= 4 else "#f6f8fb")
        self._arrow(252, 143, 280, 143)
        if stage == 3:
            self._token(154, 143, str(d_vals[0]), "#d8f5dc")
            self._token(174, 143, str(d_vals[1]), "#fff0c2")
            self._token(194, 143, str(d_vals[2]), "#fff0c2")
        elif stage >= 4:
            self._token(266, 143, str(r.dat_feedback), "#bfe8c5")

        # Shrinking decision row
        self.create_text(16, 188, text="Shrinking decision uses current output bits", anchor="w", font=("Segoe UI", 8, "bold"), fill="#333")
        self._draw_box(18, 208, 115, 246, "current selector\nr31(0)={} ".format(r.sel_bit), fill="#d8f5dc")
        self._draw_box(18, 270, 115, 308, "current data\nr32(0)={} ".format(r.dat_bit), fill="#c9edff")
        self._draw_box(160, 225, 238, 290, "r31(0)\n== 1 ?", fill="#eaf2f8", bold=True)
        out_fill = "#d8f5dc" if r.accepted else "#ffd9d9"
        out_text = "POOL\n+{}".format(r.dat_bit) if r.accepted else "DISCARD\n{}".format(r.dat_bit)
        self._draw_box(275, 238, w-18, 278, out_text, fill=out_fill, bold=True)
        self._arrow(115, 227, 160, 245)
        self._arrow(115, 289, 160, 270)
        self._arrow(238, 258, 275, 258, fill="#168a3a" if r.accepted else "#b00020", width=3)
        if stage == 5:
            self._token(138, 236, str(r.sel_bit), "#d8f5dc")
            self._token(138, 280, str(r.dat_bit), "#c9edff")
        elif stage >= 6:
            self._token(257, 258, str(r.dat_bit), "#95e0a3" if r.accepted else "#ffb3b3")

        # A compact pool is kept inside this animation panel so the accepted bits
        # are visible even when the larger Output Pool area is outside the screen.
        if stage >= 6:
            self._draw_pool_preview(313, pool_bits, highlight_last=r.accepted)

        if stage >= 7:
            msg = "ACCEPT: r31(0)=1, data bit was written to the pool." if r.accepted else "DISCARD: r31(0)=0, data bit was ignored; pool is unchanged."
            color = "#168a3a" if r.accepted else "#b00020"
            self.create_text(w/2, 382, text=msg, anchor="center", font=("Segoe UI", 8, "bold"), fill=color, width=w-20)


class ShrinkingSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1420x900")
        self.minsize(1200, 760)

        self.sel_lfsr = LFSR(31, [0, 3])
        self.dat_lfsr = LFSR(32, [0, 1, 2, 22])
        self.cycle = 0
        self.accepted_count = 0
        self.discarded_count = 0
        self.pool_bits: List[str] = []
        self.running = False
        self.after_id = None

        self._setup_style()
        self._build_ui()
        self._refresh_all()

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"), foreground="#0b1f5f")
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#0b1f5f")
        style.configure("Big.TButton", font=("Segoe UI", 10, "bold"), padding=7)
        style.configure("Stat.TLabel", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="VHDL behavior: decision uses current r(0); feedback is inserted to MSB for next state", foreground="#555").pack(side="right")

        top = ttk.Frame(root)
        top.pack(fill="x")

        seeds = ttk.LabelFrame(top, text="Seeds and Controls", style="Section.TLabelframe", padding=8)
        seeds.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Label(seeds, text="31-bit selector seed:").grid(row=0, column=0, sticky="w")
        self.sel_seed_var = tk.StringVar(value="0x7FFFFFFF")
        ttk.Entry(seeds, textvariable=self.sel_seed_var, width=38, font=("Consolas", 10)).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Label(seeds, text="taps: bit0 ⊕ bit3").grid(row=0, column=2, sticky="w", padx=6)

        ttk.Label(seeds, text="32-bit data seed:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.dat_seed_var = tk.StringVar(value="0xFFFFFFFF")
        ttk.Entry(seeds, textvariable=self.dat_seed_var, width=38, font=("Consolas", 10)).grid(row=1, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Label(seeds, text="taps: bit0 ⊕ bit1 ⊕ bit2 ⊕ bit22").grid(row=1, column=2, sticky="w", padx=6, pady=(6, 0))

        help_text = "Accepted formats: binary, 0b..., decimal, or 0x...   |   All-zero seed is replaced with all ones, same as VHDL."
        ttk.Label(seeds, text=help_text, foreground="#555").grid(row=2, column=0, columnspan=3, sticky="w", pady=(7, 0))
        seeds.columnconfigure(1, weight=1)

        buttons = ttk.LabelFrame(top, text="Run", style="Section.TLabelframe", padding=8)
        buttons.pack(side="right", fill="y")
        ttk.Button(buttons, text="Load Seeds", command=self.load_seeds, style="Big.TButton").grid(row=0, column=0, padx=4, pady=2, sticky="ew")
        ttk.Button(buttons, text="Step Clock", command=self.step_once, style="Big.TButton").grid(row=0, column=1, padx=4, pady=2, sticky="ew")
        self.auto_btn = ttk.Button(buttons, text="Auto Run", command=self.toggle_auto, style="Big.TButton")
        self.auto_btn.grid(row=1, column=0, padx=4, pady=2, sticky="ew")
        ttk.Button(buttons, text="Clear Pool", command=self.clear_pool, style="Big.TButton").grid(row=1, column=1, padx=4, pady=2, sticky="ew")
        ttk.Label(buttons, text="Speed").grid(row=2, column=0, sticky="e", pady=(6, 0))
        self.speed_var = tk.IntVar(value=450)
        ttk.Scale(buttons, from_=1000, to=60, orient="horizontal", variable=self.speed_var).grid(row=2, column=1, sticky="ew", padx=4, pady=(6, 0))

        mid = ttk.Frame(root)
        mid.pack(fill="both", expand=True, pady=(8, 0))

        left = ttk.Frame(mid)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.selector_canvas = RegisterCanvas(left, "31-bit Selector LFSR", 31, [0, 3])
        self.selector_canvas.pack(fill="x", pady=(0, 8))
        self.data_canvas = RegisterCanvas(left, "32-bit Data LFSR", 32, [0, 1, 2, 22])
        self.data_canvas.pack(fill="x", pady=(0, 8))

        decision = ttk.LabelFrame(left, text="Current Clock Cycle", style="Section.TLabelframe", padding=8)
        decision.pack(fill="x", pady=(0, 8))
        self.decision_var = tk.StringVar(value="Press Step Clock to advance one cycle.")
        self.decision_label = ttk.Label(decision, textvariable=self.decision_var, font=("Segoe UI", 12, "bold"), foreground="#0b1f5f")
        self.decision_label.pack(anchor="w")
        self.detail_var = tk.StringVar(value="Both LFSRs are clocked simultaneously. Shrinking decision uses the current selector output r31(0), not the feedback bit.")
        ttk.Label(decision, textvariable=self.detail_var, wraplength=850).pack(anchor="w", pady=(4, 0))

        hist_frame = ttk.LabelFrame(left, text="Step History", style="Section.TLabelframe", padding=6)
        hist_frame.pack(fill="both", expand=True)
        columns = ("cycle", "sel", "data", "sel_fb", "dat_fb", "valid", "bit_o", "action", "pool")
        self.history = ttk.Treeview(hist_frame, columns=columns, show="headings", height=8)
        headings = {
            "cycle": "Cycle", "sel": "Selector", "data": "Data", "sel_fb": "Sel FB", "dat_fb": "Dat FB",
            "valid": "valid_o", "bit_o": "bit_o", "action": "Action", "pool": "Pool Size"
        }
        widths = {"cycle": 60, "sel": 75, "data": 70, "sel_fb": 70, "dat_fb": 70, "valid": 70, "bit_o": 60, "action": 210, "pool": 75}
        for col in columns:
            self.history.heading(col, text=headings[col])
            self.history.column(col, width=widths[col], anchor="center")
        self.history.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(hist_frame, orient="vertical", command=self.history.yview)
        scrollbar.pack(side="right", fill="y")
        self.history.configure(yscrollcommand=scrollbar.set)

        right = ttk.Frame(mid, width=370)
        right.pack(side="right", fill="y")

        stats = ttk.LabelFrame(right, text="Live Status", style="Section.TLabelframe", padding=10)
        stats.pack(fill="x")
        self.cycle_var = tk.StringVar(value="0")
        self.accepted_var = tk.StringVar(value="0")
        self.discarded_var = tk.StringVar(value="0")
        self.rate_var = tk.StringVar(value="0.00%")
        self.sel_hex_var = tk.StringVar(value="")
        self.dat_hex_var = tk.StringVar(value="")
        self._stat_row(stats, 0, "Clock cycles:", self.cycle_var)
        self._stat_row(stats, 1, "Accepted bits:", self.accepted_var)
        self._stat_row(stats, 2, "Discarded bits:", self.discarded_var)
        self._stat_row(stats, 3, "Output rate:", self.rate_var)
        self._stat_row(stats, 4, "Selector state:", self.sel_hex_var)
        self._stat_row(stats, 5, "Data state:", self.dat_hex_var)

        flow = ttk.LabelFrame(right, text="XOR and Data Flow", style="Section.TLabelframe", padding=8)
        flow.pack(fill="x", pady=(8, 0))
        self.flow_canvas = FlowAnimationCanvas(flow, width=350, height=405)
        self.flow_canvas.pack(fill="x")

        rules = ttk.LabelFrame(right, text="Shrinking Rule", style="Section.TLabelframe", padding=10)
        rules.pack(fill="x", pady=(8, 0))
        rule_text = (
            "1) Both LFSRs produce one bit.\n"
            "2) selector = r31(0).\n"
            "3) data = r32(0).\n"
            "4) if selector = 1 → data is collected.\n"
            "5) if selector = 0 → data is discarded."
        )
        ttk.Label(rules, text=rule_text, justify="left", wraplength=340).pack(anchor="w")

        pool = ttk.LabelFrame(right, text="Output Pool", style="Section.TLabelframe", padding=8)
        pool.pack(fill="both", expand=True, pady=(8, 0))
        self.pool_text = tk.Text(pool, width=36, height=8, wrap="word", font=("Consolas", 10), background="#fbfbfb")
        self.pool_text.pack(fill="both", expand=True)
        pool_buttons = ttk.Frame(pool)
        pool_buttons.pack(fill="x", pady=(6, 0))
        ttk.Button(pool_buttons, text="Copy", command=self.copy_pool).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(pool_buttons, text="Save .txt", command=self.save_pool).pack(side="right", fill="x", expand=True, padx=(3, 0))

        footer = ttk.Label(root, text="Educational simulator for the exact VHDL implementation: PRBS31 taps bit0/bit3, PRBS32 taps bit0/bit1/bit2/bit22.", foreground="#555")
        footer.pack(fill="x", pady=(7, 0))

    def _stat_row(self, parent, row, name, var):
        ttk.Label(parent, text=name).grid(row=row, column=0, sticky="w", pady=2)
        ttk.Label(parent, textvariable=var, style="Stat.TLabel").grid(row=row, column=1, sticky="e", pady=2)
        parent.columnconfigure(1, weight=1)

    def load_seeds(self):
        try:
            sel_seed = parse_seed(self.sel_seed_var.get(), 31)
            dat_seed = parse_seed(self.dat_seed_var.get(), 32)
        except Exception as exc:
            messagebox.showerror("Invalid seed", str(exc))
            return

        replaced_sel = self.sel_lfsr.load(sel_seed)
        replaced_dat = self.dat_lfsr.load(dat_seed)
        self.cycle = 0
        self.accepted_count = 0
        self.discarded_count = 0
        self.pool_bits.clear()
        self.history.delete(*self.history.get_children())
        self.running = False
        self.auto_btn.configure(text="Auto Run")

        notes = []
        if replaced_sel:
            notes.append("Selector seed was zero and replaced with all ones.")
        if replaced_dat:
            notes.append("Data seed was zero and replaced with all ones.")
        if notes:
            messagebox.showinfo("Zero seed protection", "\n".join(notes))

        self.decision_var.set("Seeds loaded. Ready for step-by-step simulation.")
        self.detail_var.set("Press Step Clock to observe selector, data, feedback taps, and output-pool decision.")
        self.flow_canvas.draw_idle("Seeds loaded. Press Step Clock to start the visual XOR flow.")
        self._refresh_all()

    def _simulate_one_cycle(self) -> StepResult:
        self.cycle += 1
        sel_before, sel_bit, sel_feedback, sel_after = self.sel_lfsr.step()
        dat_before, dat_bit, dat_feedback, dat_after = self.dat_lfsr.step()
        accepted = sel_bit == 1
        output_bit = dat_bit if accepted else 0
        if accepted:
            self.accepted_count += 1
            self.pool_bits.append(str(dat_bit))
        else:
            self.discarded_count += 1
        return StepResult(
            cycle=self.cycle,
            sel_before=sel_before,
            dat_before=dat_before,
            sel_bit=sel_bit,
            dat_bit=dat_bit,
            sel_feedback=sel_feedback,
            dat_feedback=dat_feedback,
            sel_after=sel_after,
            dat_after=dat_after,
            accepted=accepted,
            output_bit=output_bit,
        )

    def step_once(self):
        result = self._simulate_one_cycle()
        self._show_result(result)
        self._refresh_all(result)
        self.flow_canvas.animate(result, self.pool_bits)

    def _show_result(self, result: StepResult):
        if result.accepted:
            self.decision_var.set("Cycle {}: selector = 1 → data bit {} was ACCEPTED into the output pool.".format(result.cycle, result.dat_bit))
            self.detail_var.set(
                "selector bit = r31(0) = {} | data bit = r32(0) = {} | valid_o = 1 | bit_o = {}".format(
                    result.sel_bit, result.dat_bit, result.output_bit
                )
            )
            action = "ACCEPT data bit"
        else:
            self.decision_var.set("Cycle {}: selector = 0 → data bit {} was DISCARDED.".format(result.cycle, result.dat_bit))
            self.detail_var.set(
                "selector bit = r31(0) = {} | data bit = r32(0) = {} | valid_o = 0 | bit_o = 0 placeholder".format(
                    result.sel_bit, result.dat_bit
                )
            )
            action = "DISCARD data bit"

        self.history.insert(
            "",
            0,
            values=(
                result.cycle,
                result.sel_bit,
                result.dat_bit,
                result.sel_feedback,
                result.dat_feedback,
                1 if result.accepted else 0,
                result.output_bit,
                action,
                len(self.pool_bits),
            ),
        )
        # Keep history compact.
        children = self.history.get_children()
        if len(children) > 120:
            self.history.delete(children[-1])

    def toggle_auto(self):
        self.running = not self.running
        self.auto_btn.configure(text="Pause" if self.running else "Auto Run")
        if self.running:
            self._auto_loop()
        elif self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

    def _auto_loop(self):
        if not self.running:
            return
        self.step_once()
        self.after_id = self.after(int(self.speed_var.get()), self._auto_loop)

    def clear_pool(self):
        self.pool_bits.clear()
        self.accepted_count = 0
        self.discarded_count = 0
        self.cycle = 0
        self.history.delete(*self.history.get_children())
        self.decision_var.set("Output pool and counters were cleared. Current LFSR states were kept.")
        self.detail_var.set("Press Step Clock to continue from the current internal states.")
        self.flow_canvas.draw_idle("Output pool cleared. Continue stepping from the current states.")
        self._refresh_all()

    def _refresh_all(self, result: Optional[StepResult] = None):
        sel_feedback = self.sel_lfsr.feedback_bit() if result is None else result.sel_feedback
        dat_feedback = self.dat_lfsr.feedback_bit() if result is None else result.dat_feedback
        self.selector_canvas.draw(self.sel_lfsr.state, sel_feedback)
        self.data_canvas.draw(self.dat_lfsr.state, dat_feedback)

        self.cycle_var.set(str(self.cycle))
        self.accepted_var.set(str(self.accepted_count))
        self.discarded_var.set(str(self.discarded_count))
        rate = (self.accepted_count / self.cycle * 100.0) if self.cycle else 0.0
        self.rate_var.set("{:.2f}%".format(rate))
        self.sel_hex_var.set(self.sel_lfsr.hex_string())
        self.dat_hex_var.set(self.dat_lfsr.hex_string())
        self._refresh_pool_text()

    def _refresh_pool_text(self):
        raw = "".join(self.pool_bits)
        grouped = " ".join(raw[i:i + 8] for i in range(0, len(raw), 8))
        self.pool_text.configure(state="normal")
        self.pool_text.delete("1.0", "end")
        if grouped:
            self.pool_text.insert("1.0", grouped)
        else:
            self.pool_text.insert("1.0", "No output bits collected yet.")
        self.pool_text.configure(state="disabled")

    def copy_pool(self):
        raw = "".join(self.pool_bits)
        self.clipboard_clear()
        self.clipboard_append(raw)
        self.update()
        messagebox.showinfo("Copied", "Output pool copied to clipboard.")

    def save_pool(self):
        raw = "".join(self.pool_bits)
        filename = filedialog.asksaveasfilename(
            title="Save output keystream",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if not filename:
            return
        with open(filename, "w", encoding="utf-8") as f:
            f.write(raw + "\n")
        messagebox.showinfo("Saved", "Output pool saved successfully.")


if __name__ == "__main__":
    app = ShrinkingSimulatorApp()
    app.mainloop()
