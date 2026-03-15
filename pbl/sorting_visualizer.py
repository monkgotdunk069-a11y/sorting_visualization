"""
╔══════════════════════════════════════════════════════════════════╗
║         SORTING VISUALIZER  –  Real-Time Algorithm Demo          ║
║  Libraries: tkinter · matplotlib · numpy · pandas               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

# ─────────────────────────────── THEME ────────────────────────────────
BG_DARK    = "#0F1117"
BG_PANEL   = "#1A1D2E"
BG_CARD    = "#21253A"
ACCENT     = "#6C63FF"
ACCENT2    = "#FF6584"
TEXT_MAIN  = "#EAEAEA"
TEXT_DIM   = "#7C7F9E"
COLOR_DEFAULT  = "#5C6BC0"
COLOR_COMPARE  = "#FFC107"
COLOR_SWAP     = "#F44336"
COLOR_SORTED   = "#4CAF50"
COLOR_PIVOT    = "#FF9800"

FONT_TITLE  = ("Segoe UI", 16, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)


# ──────────────────────────── SORTING ALGORITHMS ──────────────────────
def bubble_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(n - i - 1):
            yield a.copy(), [j, j+1], "compare", 0, 0
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]
                yield a.copy(), [j, j+1], "swap", 1, 1
        yield a.copy(), [n-1-i], "sorted_mark", 0, 0
    yield a.copy(), list(range(n)), "done", 0, 0


def selection_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            yield a.copy(), [min_idx, j], "compare", 0, 0
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            yield a.copy(), [i, min_idx], "swap", 1, 1
        yield a.copy(), [i], "sorted_mark", 0, 0
    yield a.copy(), list(range(n)), "done", 0, 0


def insertion_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0:
            yield a.copy(), [j, j+1], "compare", 0, 0
            if a[j] > key:
                a[j+1] = a[j]
                j -= 1
                yield a.copy(), [j+1], "swap", 0, 1
            else:
                break
        a[j+1] = key
        yield a.copy(), [j+1], "sorted_mark", 0, 0
    yield a.copy(), list(range(n)), "done", 0, 0


def merge_sort(arr):
    a = arr.copy()
    yield from _merge_sort_helper(a, 0, len(a) - 1)
    yield a.copy(), list(range(len(a))), "done", 0, 0


def _merge_sort_helper(a, l, r):
    if l >= r:
        return
    mid = (l + r) // 2
    yield from _merge_sort_helper(a, l, mid)
    yield from _merge_sort_helper(a, mid+1, r)
    yield from _merge(a, l, mid, r)


def _merge(a, l, mid, r):
    left = a[l:mid+1].copy()
    right = a[mid+1:r+1].copy()
    i = j = 0
    k = l
    while i < len(left) and j < len(right):
        yield a.copy(), [l+i, mid+1+j], "compare", 0, 0
        if left[i] <= right[j]:
            a[k] = left[i]; i += 1
        else:
            a[k] = right[j]; j += 1
        yield a.copy(), [k], "swap", 0, 1
        k += 1
    while i < len(left):
        a[k] = left[i]; i += 1; k += 1
        yield a.copy(), [k-1], "swap", 0, 1
    while j < len(right):
        a[k] = right[j]; j += 1; k += 1
        yield a.copy(), [k-1], "swap", 0, 1


def quick_sort(arr):
    a = arr.copy()
    yield from _quick_sort_helper(a, 0, len(a)-1)
    yield a.copy(), list(range(len(a))), "done", 0, 0


def _quick_sort_helper(a, low, high):
    if low < high:
        yield from _partition(a, low, high)
        pi_holder = [0]
        # re-run partition to get pi (store result differently)
        temp = a.copy()
        pivot = temp[high]
        i = low - 1
        for j in range(low, high):
            if temp[j] <= pivot:
                i += 1
                temp[i], temp[j] = temp[j], temp[i]
        temp[i+1], temp[high] = temp[high], temp[i+1]
        pi = i + 1
        yield from _quick_sort_helper(a, low, pi - 1)
        yield from _quick_sort_helper(a, pi + 1, high)


def _partition(a, low, high):
    pivot = a[high]
    i = low - 1
    for j in range(low, high):
        yield a.copy(), [j, high], "compare", 0, 0
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            yield a.copy(), [i, j], "swap", 1, 1
    a[i+1], a[high] = a[high], a[i+1]
    yield a.copy(), [i+1], "sorted_mark", 0, 0


def heap_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n//2 - 1, -1, -1):
        yield from _heapify(a, n, i)
    for i in range(n-1, 0, -1):
        a[0], a[i] = a[i], a[0]
        yield a.copy(), [0, i], "swap", 1, 1
        yield from _heapify(a, i, 0)
    yield a.copy(), list(range(n)), "done", 0, 0


def _heapify(a, n, i):
    largest = i
    l, r = 2*i+1, 2*i+2
    if l < n:
        yield a.copy(), [largest, l], "compare", 0, 0
        if a[l] > a[largest]:
            largest = l
    if r < n:
        yield a.copy(), [largest, r], "compare", 0, 0
        if a[r] > a[largest]:
            largest = r
    if largest != i:
        a[i], a[largest] = a[largest], a[i]
        yield a.copy(), [i, largest], "swap", 1, 1
        yield from _heapify(a, n, largest)


ALGORITHMS = {
    "Bubble Sort":    bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort":     merge_sort,
    "Quick Sort":     quick_sort,
    "Heap Sort":      heap_sort,
}

COMPLEXITY = {
    "Bubble Sort":    ("O(n²)", "O(n²)",    "O(1)"),
    "Selection Sort": ("O(n²)", "O(n²)",    "O(1)"),
    "Insertion Sort": ("O(n)",  "O(n²)",    "O(1)"),
    "Merge Sort":     ("O(n log n)", "O(n log n)", "O(n)"),
    "Quick Sort":     ("O(n log n)", "O(n²)", "O(log n)"),
    "Heap Sort":      ("O(n log n)", "O(n log n)", "O(1)"),
}


# ──────────────────────────────── MAIN APP ─────────────────────────────
class SortingVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Sorting Visualizer  |  Real-Time Algorithm Demo")
        self.geometry("1280x820")
        self.minsize(1080, 720)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # State
        self.array         = np.array([])
        self.sorted_indices = set()
        self.is_sorting    = False
        self.is_paused     = False
        self.current_gen   = None
        self.after_id      = None
        self.comparisons   = 0
        self.swaps         = 0
        self.start_time    = 0
        self.score_df      = pd.DataFrame(columns=[
            "Algorithm", "Size", "Array Type",
            "Comparisons", "Swaps", "Time (s)"
        ])

        self._build_ui()
        self._generate_array()

    # ── UI Construction ──────────────────────────────────────────────
    def _build_ui(self):
        # ── Title bar ──
        title_frame = tk.Frame(self, bg=BG_PANEL, height=52)
        title_frame.pack(fill="x", side="top")
        tk.Label(title_frame, text="⚡ SORTING VISUALIZER",
                 font=("Segoe UI", 17, "bold"), fg=ACCENT, bg=BG_PANEL
                 ).pack(side="left", padx=20, pady=10)
        tk.Label(title_frame, text="Real-Time Algorithm Demo  |  matplotlib · numpy · pandas",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=BG_PANEL
                 ).pack(side="left", padx=5, pady=10)

        # ── Main content ──
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=10, pady=(0,5))

        # Left sidebar
        self.sidebar = tk.Frame(main, bg=BG_PANEL, width=240)
        self.sidebar.pack(side="left", fill="y", padx=(0,8), pady=4)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Center (chart + stats strip)
        center = tk.Frame(main, bg=BG_DARK)
        center.pack(side="left", fill="both", expand=True)

        # Stats strip
        self.stats_frame = tk.Frame(center, bg=BG_PANEL, height=56)
        self.stats_frame.pack(fill="x", pady=(4,6))
        self._build_stats_strip()

        # Matplotlib chart
        chart_frame = tk.Frame(center, bg=BG_DARK)
        chart_frame.pack(fill="both", expand=True)
        self._build_chart(chart_frame)

        # Scoreboard (bottom)
        sb_frame = tk.Frame(center, bg=BG_PANEL, height=170)
        sb_frame.pack(fill="x", pady=(6,0))
        sb_frame.pack_propagate(False)
        self._build_scoreboard(sb_frame)

    def _build_sidebar(self):
        pad = dict(padx=14, pady=5)

        tk.Label(self.sidebar, text="ALGORITHM", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(anchor="w", **pad)
        self.algo_var = tk.StringVar(value="Bubble Sort")
        algo_cb = ttk.Combobox(self.sidebar, textvariable=self.algo_var,
                               values=list(ALGORITHMS.keys()), state="readonly",
                               font=FONT_BODY)
        algo_cb.pack(fill="x", padx=14, pady=(0,8))
        algo_cb.bind("<<ComboboxSelected>>", lambda e: self._update_complexity())

        tk.Label(self.sidebar, text="ARRAY TYPE", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(anchor="w", **pad)
        self.arr_type_var = tk.StringVar(value="Random")
        arr_cb = ttk.Combobox(self.sidebar, textvariable=self.arr_type_var,
                              values=["Random", "Nearly Sorted", "Reversed", "Few Unique"],
                              state="readonly", font=FONT_BODY)
        arr_cb.pack(fill="x", padx=14, pady=(0,8))

        tk.Label(self.sidebar, text="ARRAY SIZE", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(anchor="w", **pad)
        self.size_var = tk.IntVar(value=50)
        self.size_label = tk.Label(self.sidebar, text="50",
                                   font=FONT_MONO, fg=TEXT_MAIN, bg=BG_PANEL)
        self.size_label.pack(anchor="e", padx=18)
        size_slider = ttk.Scale(self.sidebar, from_=10, to=150,
                                variable=self.size_var, orient="horizontal",
                                command=lambda v: self.size_label.config(text=str(int(float(v)))))
        size_slider.pack(fill="x", padx=14, pady=(0,10))

        tk.Label(self.sidebar, text="SPEED", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(anchor="w", **pad)
        self.speed_var = tk.IntVar(value=50)
        self.speed_label = tk.Label(self.sidebar, text="50 ms",
                                    font=FONT_MONO, fg=TEXT_MAIN, bg=BG_PANEL)
        self.speed_label.pack(anchor="e", padx=18)
        speed_slider = ttk.Scale(self.sidebar, from_=1, to=200,
                                 variable=self.speed_var, orient="horizontal",
                                 command=lambda v: self.speed_label.config(
                                     text=f"{int(float(v))} ms"))
        speed_slider.pack(fill="x", padx=14, pady=(0,14))

        # Buttons
        def btn(text, cmd, color):
            b = tk.Button(self.sidebar, text=text, command=cmd,
                          bg=color, fg="white", font=("Segoe UI", 10, "bold"),
                          relief="flat", cursor="hand2", pady=8,
                          activebackground=color, activeforeground="white",
                          bd=0, highlightthickness=0)
            b.pack(fill="x", padx=14, pady=4)
            return b

        btn("🎲  Generate Array", self._generate_array, "#3949AB")
        self.sort_btn = btn("▶  Start Sort", self._start_sort, ACCENT)
        self.pause_btn = btn("⏸  Pause / Resume", self._toggle_pause, "#546E7A")
        btn("⏹  Reset", self._reset, ACCENT2)

        # Complexity card
        sep = tk.Frame(self.sidebar, bg=BG_CARD, height=2)
        sep.pack(fill="x", padx=14, pady=(14,8))
        tk.Label(self.sidebar, text="COMPLEXITY", font=("Segoe UI", 9, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(anchor="w", padx=14)
        self.cx_frame = tk.Frame(self.sidebar, bg=BG_CARD, bd=0)
        self.cx_frame.pack(fill="x", padx=14, pady=6)
        self.cx_best  = self._cx_row("Best",  "—")
        self.cx_worst = self._cx_row("Worst", "—")
        self.cx_space = self._cx_row("Space", "—")
        self._update_complexity()

    def _cx_row(self, label, val):
        row = tk.Frame(self.cx_frame, bg=BG_CARD)
        row.pack(fill="x", padx=6, pady=2)
        tk.Label(row, text=label+":", font=FONT_SMALL,
                 fg=TEXT_DIM, bg=BG_CARD, width=6, anchor="w").pack(side="left")
        v = tk.Label(row, text=val, font=("Consolas", 10, "bold"),
                     fg=COLOR_COMPARE, bg=BG_CARD)
        v.pack(side="left")
        return v

    def _update_complexity(self):
        algo = self.algo_var.get()
        best, worst, space = COMPLEXITY.get(algo, ("—","—","—"))
        self.cx_best.config(text=best)
        self.cx_worst.config(text=worst)
        self.cx_space.config(text=space)

    def _build_stats_strip(self):
        stats = [
            ("⚙  COMPARISONS", "cmp_lbl", "0"),
            ("🔄  SWAPS",       "swp_lbl", "0"),
            ("⏱  TIME",        "time_lbl", "0.000 s"),
            ("📐  ARRAY SIZE",  "sz_lbl",  "—"),
            ("🏷  ALGORITHM",   "alg_lbl", "—"),
        ]
        for title, attr, default in stats:
            card = tk.Frame(self.stats_frame, bg=BG_CARD,
                            padx=14, pady=6)
            card.pack(side="left", padx=6, pady=6, fill="y")
            tk.Label(card, text=title, font=("Segoe UI", 8, "bold"),
                     fg=TEXT_DIM, bg=BG_CARD).pack(anchor="w")
            lbl = tk.Label(card, text=default, font=("Consolas", 13, "bold"),
                           fg=TEXT_MAIN, bg=BG_CARD)
            lbl.pack(anchor="w")
            setattr(self, attr, lbl)

    def _build_chart(self, parent):
        self.fig = Figure(figsize=(8, 4.2), facecolor=BG_DARK)
        self.ax  = self.fig.add_subplot(111)
        self._style_ax()
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.draw()

    def _style_ax(self):
        self.ax.set_facecolor(BG_DARK)
        self.ax.tick_params(colors=TEXT_DIM, labelsize=7)
        self.ax.spines["bottom"].set_color(BG_CARD)
        self.ax.spines["left"].set_color(BG_CARD)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_xticklabels([])
        self.ax.set_ylabel("Value", color=TEXT_DIM, fontsize=8)

    def _build_scoreboard(self, parent):
        header = tk.Frame(parent, bg=BG_PANEL)
        header.pack(fill="x", padx=10, pady=(6,2))
        tk.Label(header, text="🏆  SCOREBOARD", font=("Segoe UI", 10, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(side="left")
        tk.Button(header, text="Clear", command=self._clear_scores,
                  bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL, relief="flat",
                  cursor="hand2", bd=0, padx=8, pady=2).pack(side="right", padx=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Score.Treeview",
                         background=BG_CARD, foreground=TEXT_MAIN,
                         fieldbackground=BG_CARD, rowheight=24,
                         font=FONT_SMALL)
        style.configure("Score.Treeview.Heading",
                         background=BG_PANEL, foreground=ACCENT,
                         font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Score.Treeview", background=[("selected", ACCENT)])

        cols = ["#", "Algorithm", "Size", "Array Type",
                "Comparisons", "Swaps", "Time (s)"]
        self.tree = ttk.Treeview(parent, columns=cols, show="headings",
                                 style="Score.Treeview", height=5)
        widths = [30, 130, 60, 110, 110, 80, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_score_col(c))
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0,6))

        sb = ttk.Scrollbar(parent, orient="horizontal",
                           command=self.tree.xview)
        self.tree.configure(xscrollcommand=sb.set)

    # ── Array Generation ─────────────────────────────────────────────
    def _generate_array(self):
        if self.is_sorting:
            return
        self._reset_state()
        n = int(self.size_var.get())
        arr_type = self.arr_type_var.get()
        if arr_type == "Random":
            self.array = np.random.randint(5, 500, n)
        elif arr_type == "Nearly Sorted":
            self.array = np.sort(np.random.randint(5, 500, n))
            swaps = max(1, n // 10)
            for _ in range(swaps):
                i, j = np.random.choice(n, 2, replace=False)
                self.array[i], self.array[j] = self.array[j], self.array[i]
        elif arr_type == "Reversed":
            self.array = np.sort(np.random.randint(5, 500, n))[::-1].copy()
        elif arr_type == "Few Unique":
            unique_vals = np.random.randint(5, 500, max(3, n//10))
            self.array = np.random.choice(unique_vals, n)
        self.sorted_indices = set()
        self.sz_lbl.config(text=str(n))
        self.alg_lbl.config(text=self.algo_var.get())
        self._draw_array(self.array, [], "default")

    # ── Chart Drawing ────────────────────────────────────────────────
    def _draw_array(self, arr, highlight_idx, state):
        self.ax.clear()
        self._style_ax()
        n = len(arr)
        colors = []
        for i in range(n):
            if i in self.sorted_indices or state == "done":
                colors.append(COLOR_SORTED)
            elif i in highlight_idx:
                if state == "swap":
                    colors.append(COLOR_SWAP)
                elif state == "compare":
                    colors.append(COLOR_COMPARE)
                elif state == "sorted_mark":
                    colors.append(COLOR_SORTED)
                else:
                    colors.append(COLOR_PIVOT)
            else:
                colors.append(COLOR_DEFAULT)

        self.ax.bar(range(n), arr, color=colors,
                    edgecolor="none", width=1.0)
        self.ax.set_xlim(-0.5, n - 0.5)
        self.ax.set_ylim(0, arr.max() * 1.08 if len(arr) > 0 else 500)

        # Legend (only draw once, small)
        legend_items = [
            plt.Rectangle((0,0),1,1, color=COLOR_DEFAULT,  label="Default"),
            plt.Rectangle((0,0),1,1, color=COLOR_COMPARE,  label="Comparing"),
            plt.Rectangle((0,0),1,1, color=COLOR_SWAP,     label="Swapping"),
            plt.Rectangle((0,0),1,1, color=COLOR_SORTED,   label="Sorted"),
        ]
        self.ax.legend(handles=legend_items, loc="upper right",
                       facecolor=BG_PANEL, edgecolor="none",
                       labelcolor=TEXT_MAIN, fontsize=7,
                       framealpha=0.85, ncol=4)
        self.canvas.draw_idle()

    # ── Sort Control ─────────────────────────────────────────────────
    def _start_sort(self):
        if self.is_sorting:
            return
        if len(self.array) == 0:
            self._generate_array()
        self.is_sorting  = True
        self.is_paused   = False
        self.comparisons = 0
        self.swaps       = 0
        self.start_time  = time.perf_counter()
        self.sorted_indices = set()
        algo = self.algo_var.get()
        self.alg_lbl.config(text=algo)
        self.current_gen = ALGORITHMS[algo](self.array.copy())
        self._step()

    def _step(self):
        if not self.is_sorting:
            return
        if self.is_paused:
            self.after_id = self.after(100, self._step)
            return
        try:
            arr, highlight, state, cmp_inc, swp_inc = next(self.current_gen)
            self.comparisons += cmp_inc
            self.swaps       += swp_inc
            if state == "sorted_mark":
                for idx in highlight:
                    self.sorted_indices.add(idx)
            elapsed = time.perf_counter() - self.start_time
            self.cmp_lbl.config(text=f"{self.comparisons:,}")
            self.swp_lbl.config(text=f"{self.swaps:,}")
            self.time_lbl.config(text=f"{elapsed:.3f} s")
            self._draw_array(arr, highlight, state)
            delay = max(1, int(self.speed_var.get()))
            self.after_id = self.after(delay, self._step)
        except StopIteration:
            self._on_sort_done()

    def _on_sort_done(self):
        self.is_sorting = False
        elapsed = time.perf_counter() - self.start_time
        self.time_lbl.config(text=f"{elapsed:.3f} s")
        self.sorted_indices = set(range(len(self.array)))
        self._draw_array(
            sorted(self.array) if len(self.array) > 0 else self.array,
            list(range(len(self.array))), "done"
        )
        self._add_score(elapsed)

    def _toggle_pause(self):
        if not self.is_sorting:
            return
        self.is_paused = not self.is_paused

    def _reset(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        self._reset_state()
        self._generate_array()

    def _reset_state(self):
        self.is_sorting     = False
        self.is_paused      = False
        self.comparisons    = 0
        self.swaps          = 0
        self.cmp_lbl.config(text="0")
        self.swp_lbl.config(text="0")
        self.time_lbl.config(text="0.000 s")
        self.sorted_indices = set()

    # ── Scoreboard ───────────────────────────────────────────────────
    def _add_score(self, elapsed):
        new_row = {
            "Algorithm":   self.algo_var.get(),
            "Size":        int(self.size_var.get()),
            "Array Type":  self.arr_type_var.get(),
            "Comparisons": self.comparisons,
            "Swaps":       self.swaps,
            "Time (s)":    round(elapsed, 4),
        }
        self.score_df = pd.concat(
            [self.score_df, pd.DataFrame([new_row])], ignore_index=True
        )
        self._refresh_tree()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        df_sorted = self.score_df.sort_values(
            "Time (s)", ascending=True
        ).reset_index(drop=True)
        tags = ["gold", "silver", "bronze"]
        tag_colors = {"gold": "#FFD700", "silver": "#C0C0C0",
                      "bronze": "#CD7F32", "normal": TEXT_MAIN}
        for tag, col in tag_colors.items():
            self.tree.tag_configure(tag, foreground=col)
        for i, row in df_sorted.iterrows():
            tag = tags[i] if i < 3 else "normal"
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else str(i+1)
            self.tree.insert("", "end", values=(
                medal,
                row["Algorithm"],
                row["Size"],
                row["Array Type"],
                f"{int(row['Comparisons']):,}",
                f"{int(row['Swaps']):,}",
                f"{row['Time (s)']:.4f}",
            ), tags=(tag,))

    def _sort_score_col(self, col):
        """Sort scoreboard by clicked column header."""
        try:
            self.score_df = self.score_df.sort_values(
                col if col in self.score_df.columns else "Time (s)",
                ascending=True
            )
        except Exception:
            pass
        self._refresh_tree()

    def _clear_scores(self):
        self.score_df = pd.DataFrame(columns=[
            "Algorithm", "Size", "Array Type",
            "Comparisons", "Swaps", "Time (s)"
        ])
        self.tree.delete(*self.tree.get_children())


# ───────────────────────────── Entry Point ─────────────────────────────
if __name__ == "__main__":
    app = SortingVisualizer()
    app.mainloop()
