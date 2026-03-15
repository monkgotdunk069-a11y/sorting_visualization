# Premier League Stats App — Source Code Documentation
### File: `pl_stats_app.py`
### Project: PBL – Sorting Visualizer using Real-World Data
### Author Documentation Version: 1.0 | Date: March 2025

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Libraries Used](#2-libraries-used)
3. [Theme & Colour Constants](#3-theme--colour-constants)
4. [Sorting Algorithms](#4-sorting-algorithms)
5. [Complexity Table](#5-complexity-table)
6. [DataFetcher Class](#6-datafetcher-class)
7. [ExcelExporter Class](#7-excelexporter-class)
8. [PLStatsApp Class (Main Window)](#8-plstatsapp-class-main-window)
   - [__init__](#81-init--constructor)
   - [Title Bar](#82-title-bar)
   - [Tab 1 – Live Standings](#83-tab-1--live-standings)
   - [Tab 2 – Sort Visualizer](#84-tab-2--sort-visualizer)
   - [Data Loading & Threading](#85-data-loading--threading)
   - [Sorting & Filtering (Standings)](#86-sorting--filtering-standings)
   - [Excel Export](#87-excel-export)
   - [Status Bar & Spinner](#88-status-bar--spinner)
9. [Entry Point](#9-entry-point)

---

## 1. Project Overview

This application is a **Premier League Football Statistics Dashboard** built in Python. It serves as the main PBL (Project-Based Learning) project combining:

| Feature | Purpose |
|---|---|
| Web Scraping | Fetches live PL standings from the internet |
| Pandas / NumPy | Data cleaning, manipulation, computation |
| Matplotlib | Embedded bar charts inside the GUI |
| Tkinter | Desktop GUI window with two tabs |
| Sorting Algorithms | **Core topic** – animated visualization on real football data |
| Excel Export | Saves formatted data + chart to `.xlsx` |

---

## 2. Libraries Used

```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
```
- `tkinter` – Python's built-in GUI library. Used to build the entire window, buttons, tables, labels etc.
- `ttk` – Themed version of tkinter widgets (nicer-looking ComboBox, Treeview, Scrollbar etc.)
- `messagebox` – Shows popup dialogs (errors, info, warnings)
- `filedialog` – Opens the OS file-picker dialog (used for Excel Save As)

```python
import threading
```
- Python's standard threading library. Used to run web requests in the **background** so the GUI doesn't freeze while data is loading.

```python
import time
```
- Used by `time.perf_counter()` to measure how long a sort takes (high-precision timer).

```python
import requests
```
- Third-party library to make HTTP GET requests to websites (web scraping).

```python
import pandas as pd
import numpy as np
```
- `pandas` – Reads HTML tables from websites (`pd.read_html`), stores data as DataFrames, and handles sorting/filtering.
- `numpy` – Numerical operations (e.g., `np.nan` for missing values, array operations).

```python
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
```
- `matplotlib` – Python's main plotting library.
- `matplotlib.use("TkAgg")` – **Must be called before any other matplotlib import.** Tells matplotlib to use the Tkinter rendering backend so charts can be embedded inside a Tkinter window.
- `FigureCanvasTkAgg` – The bridge that embeds a matplotlib Figure into a Tkinter frame.
- `Figure` – Object-oriented way to create a matplotlib chart (more control than `plt.figure()`).

```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter
```
- `openpyxl` – Library for creating and formatting Excel `.xlsx` files.
- `PatternFill` – Fills a cell with a background colour.
- `Font` – Sets font name, size, bold, colour for a cell.
- `Alignment` – Aligns text in a cell (center, left, right).
- `Border / Side` – Draws cell borders.
- `BarChart / Reference` – Creates an embedded bar chart in the Excel file.
- `get_column_letter` – Converts column number to letter (e.g., 3 → "C").

```python
from datetime import datetime
```
- Used to get the current time (`datetime.now()`) to display "Last updated: HH:MM:SS" in the status bar.

---

## 3. Theme & Colour Constants

```python
BG_DARK    = "#0D0F1A"   # Main window background (very dark navy)
BG_PANEL   = "#151828"   # Panel/sidebar background
BG_CARD    = "#1E2235"   # Card/widget background
BG_ROW_ALT = "#181B2C"   # Alternating row colour in the table
ACCENT     = "#38003C"   # Premier League official purple
ACCENT2    = "#00FF85"   # Premier League official neon green
TEXT_MAIN  = "#EAEAEA"   # Primary text colour (near white)
TEXT_DIM   = "#7C7F9E"   # Dimmed/secondary text (grey-purple)
TEXT_GOLD  = "#FFD700"   # Gold colour (used for Leader card)
CL_COLOR   = "#1A73E8"   # Blue  – Champions League zone (top 4)
EL_COLOR   = "#FF9500"   # Orange – Europa League zone (5th-6th)
REL_COLOR  = "#E53935"   # Red   – Relegation zone (bottom 3)
MID_COLOR  = "#3A3F5C"   # Grey  – Mid-table
```

### Sort Visualizer colours:
```python
COL_DEFAULT = "#5C6BC0"  # Bar default colour (indigo)
COL_COMPARE = "#FFC107"  # Yellow – two bars being compared
COL_SWAP    = "#F44336"  # Red    – two bars being swapped
COL_SORTED  = "#4CAF50"  # Green  – bar in its final sorted position
COL_PIVOT   = "#FF9800"  # Orange – pivot element (Quick Sort)
```

### Font tuples:
```python
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_HEAD  = ("Segoe UI", 11, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 10)   # Monospace for numbers
```
Tkinter accepts fonts as `(family, size, style)` tuples.

### Request headers:
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 ...",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,...",
}
```
When scraping websites, we send browser-like headers so the server does not block us as a bot.

---

## 4. Sorting Algorithms

All six algorithms follow the same **generator pattern**:

```python
yield current_array_copy, highlight_indices, state_string, cmp_increment, swap_increment
```

Each `yield` produces one **animation frame**. The GUI reads these frames one at a time with `next()` and redraws the chart.

| Parameter | Type | Meaning |
|---|---|---|
| `current_array_copy` | `list` | Snapshot of the array at this moment |
| `highlight_indices` | `list[int]` | Indices of the bars to colour |
| `state_string` | `str` | `"compare"`, `"swap"`, `"sorted_mark"`, `"done"` |
| `cmp_increment` | `int` | 1 if this step is a comparison, else 0 |
| `swap_increment` | `int` | 1 if this step is a swap, else 0 |

---

### 4.1 Bubble Sort
```python
def bubble_sort(arr):
    a = arr.copy()       # Work on a copy so original is unchanged
    n = len(a)
    for i in range(n):               # Outer loop: n passes
        for j in range(n - i - 1):  # Inner loop: shrinks each pass (sorted tail)
            yield a.copy(), [j, j+1], "compare", 1, 0   # Highlight pair being compared
            if a[j] > a[j+1]:                           # If left > right → wrong order
                a[j], a[j+1] = a[j+1], a[j]            # Swap them
                yield a.copy(), [j, j+1], "swap", 0, 1 # Show the swap
        yield a.copy(), [n-1-i], "sorted_mark", 0, 0   # Last element of this pass is sorted
    yield a.copy(), list(range(n)), "done", 0, 0        # All sorted!
```
**How it works:** Repeatedly compares adjacent elements and swaps them if they are in the wrong order. The largest unsorted element "bubbles" to the end each pass.

---

### 4.2 Selection Sort
```python
def selection_sort(arr):
    a = arr.copy(); n = len(a)
    for i in range(n):           # i = position we are filling
        min_idx = i              # Assume current position is the minimum
        for j in range(i+1, n): # Search the rest of the array
            yield a.copy(), [min_idx, j], "compare", 1, 0
            if a[j] < a[min_idx]: min_idx = j   # Found a new minimum
        if min_idx != i:         # If minimum isn't already in place
            a[i], a[min_idx] = a[min_idx], a[i] # Swap it into position
            yield a.copy(), [i, min_idx], "swap", 0, 1
        yield a.copy(), [i], "sorted_mark", 0, 0 # Position i is now sorted
    yield a.copy(), list(range(n)), "done", 0, 0
```
**How it works:** Finds the minimum element of the unsorted portion and moves it to the front.

---

### 4.3 Insertion Sort
```python
def insertion_sort(arr):
    a = arr.copy(); n = len(a)
    for i in range(1, n):    # Start from index 1 (index 0 is already "sorted")
        key = a[i]           # The element we want to insert in the right place
        j = i - 1            # Start comparing with the element to the left
        while j >= 0:
            yield a.copy(), [j, j+1], "compare", 1, 0
            if a[j] > key:   # If left element is bigger, shift it right
                a[j+1] = a[j]; j -= 1
                yield a.copy(), [j+1], "swap", 0, 1
            else:
                break        # Found the correct position, stop
        a[j+1] = key         # Insert the key in its correct position
        yield a.copy(), [j+1], "sorted_mark", 0, 0
    yield a.copy(), list(range(n)), "done", 0, 0
```
**How it works:** Like sorting playing cards – picks each element and inserts it at the correct position in the already-sorted portion.

---

### 4.4 Merge Sort
```python
def merge_sort(arr):
    a = arr.copy()
    yield from _merge_helper(a, 0, len(a)-1)  # Recursively sort
    yield a.copy(), list(range(len(a))), "done", 0, 0
```
`yield from` passes all yields from the recursive calls up to the caller.

```python
def _merge_helper(a, l, r):    # l=left index, r=right index
    if l >= r: return          # Base case: only one element, already sorted
    mid = (l+r)//2             # Find the middle
    yield from _merge_helper(a, l, mid)      # Sort left half
    yield from _merge_helper(a, mid+1, r)   # Sort right half
    yield from _merge(a, l, mid, r)         # Merge both halves
```

```python
def _merge(a, l, mid, r):
    left  = a[l:mid+1].copy()    # Copy of left sub-array
    right = a[mid+1:r+1].copy()  # Copy of right sub-array
    i = j = 0; k = l             # i=left pointer, j=right pointer, k=position in a
    while i < len(left) and j < len(right):
        yield a.copy(), [l+i, mid+1+j], "compare", 1, 0
        if left[i] <= right[j]: a[k] = left[i]; i += 1  # Left is smaller
        else:                   a[k] = right[j]; j += 1 # Right is smaller
        yield a.copy(), [k], "swap", 0, 1; k += 1       # Show placement
    # Copy remaining elements from whichever sub-array is not exhausted
    while i < len(left):
        a[k] = left[i]; i += 1; k += 1
        yield a.copy(), [k-1], "swap", 0, 1
    while j < len(right):
        a[k] = right[j]; j += 1; k += 1
        yield a.copy(), [k-1], "swap", 0, 1
```
**How it works:** Divide the array in half recursively until each piece has one element, then merge the pieces back together in sorted order.

---

### 4.5 Quick Sort
```python
def quick_sort(arr):
    a = arr.copy()
    yield from _quick_helper(a, 0, len(a)-1)
    yield a.copy(), list(range(len(a))), "done", 0, 0
```
```python
def _quick_helper(a, low, high):
    if low < high:
        yield from _partition(a, low, high)  # Partition and show animation
        # Re-simulate the partition to get the pivot index (pi)
        temp = a.copy(); pivot = temp[high]; i = low-1
        for j in range(low, high):
            if temp[j] <= pivot: i += 1; temp[i], temp[j] = temp[j], temp[i]
        temp[i+1], temp[high] = temp[high], temp[i+1]; pi = i+1
        yield from _quick_helper(a, low, pi-1)   # Sort left of pivot
        yield from _quick_helper(a, pi+1, high)  # Sort right of pivot
```
```python
def _partition(a, low, high):
    pivot = a[high]   # Choose the last element as pivot
    i = low - 1       # i tracks the boundary of smaller elements
    for j in range(low, high):
        yield a.copy(), [j, high], "compare", 1, 0
        if a[j] <= pivot:         # Element belongs on left of pivot
            i += 1
            a[i], a[j] = a[j], a[i]   # Swap it to the left side
            yield a.copy(), [i, j], "swap", 0, 1
    a[i+1], a[high] = a[high], a[i+1]  # Place pivot in its correct position
    yield a.copy(), [i+1], "sorted_mark", 0, 0
```
**How it works:** Picks a pivot element, places all smaller elements to its left and all larger elements to its right. Recursively sorts both sides.

---

### 4.6 Heap Sort
```python
def heap_sort(arr):
    a = arr.copy(); n = len(a)
    # Phase 1: Build a max-heap (rearrange so largest is always at root)
    for i in range(n//2-1, -1, -1): yield from _heapify(a, n, i)
    # Phase 2: Extract maximum one by one
    for i in range(n-1, 0, -1):
        a[0], a[i] = a[i], a[0]   # Move current max (root) to end
        yield a.copy(), [0, i], "swap", 0, 1
        yield from _heapify(a, i, 0)  # Re-heapify the reduced heap
    yield a.copy(), list(range(n)), "done", 0, 0
```
```python
def _heapify(a, n, i):
    largest = i          # Assume root is largest
    l, r = 2*i+1, 2*i+2 # Left and right children in the heap array
    if l < n:
        yield a.copy(), [largest, l], "compare", 1, 0
        if a[l] > a[largest]: largest = l   # Left child is larger
    if r < n:
        yield a.copy(), [largest, r], "compare", 1, 0
        if a[r] > a[largest]: largest = r   # Right child is larger
    if largest != i:     # Root is NOT the largest – fix the heap
        a[i], a[largest] = a[largest], a[i]
        yield a.copy(), [i, largest], "swap", 0, 1
        yield from _heapify(a, n, largest)  # Recursively fix affected subtree
```
**How it works:** Converts the array into a max-heap tree structure, then repeatedly extracts the maximum element to produce a sorted array.

---

## 5. Complexity Table

```python
ALGORITHMS = {
    "Bubble Sort":    bubble_sort,
    "Selection Sort": selection_sort,
    ...
}
```
A dictionary mapping algorithm names (strings) → their generator functions. Used to call the right algorithm when user selects from the dropdown.

```python
COMPLEXITY = {
    "Bubble Sort":    ("O(n)",       "O(n²)",       "O(1)"),
    "Selection Sort": ("O(n²)",      "O(n²)",       "O(1)"),
    "Insertion Sort": ("O(n)",       "O(n²)",       "O(1)"),
    "Merge Sort":     ("O(n log n)", "O(n log n)",  "O(n)"),
    "Quick Sort":     ("O(n log n)", "O(n²)",       "O(log n)"),
    "Heap Sort":      ("O(n log n)", "O(n log n)",  "O(1)"),
}
```
Each tuple is `(Best Case, Worst Case, Space Complexity)`. Shown in the sidebar complexity card when an algorithm is selected.

---

## 6. DataFetcher Class

```python
class DataFetcher:
    COLS       = ["Rank","Team","MP","W","D","L","GF","GA","GD","Pts"]
    EXTRA_COLS = ["xG","xGA"]
```
- `COLS` – The 10 main columns we want from the Premier League standings.
- `EXTRA_COLS` – Expected Goals (xG) and Expected Goals Against (xGA) — advanced stats.

### `fetch()` method
```python
def fetch(self):
    for fn, src in [(self._from_fbref, "fbref.com"),
                    (self._from_wikipedia, "Wikipedia")]:
        try:
            df, s = fn()
            if df is not None and len(df) >= 18:
                return df, s
        except Exception:
            pass
    return self._sample_data(), "Sample (offline)"
```
Tries each data source in order. If it gets at least 18 teams, it accepts and returns that data. If all sources fail (no internet), it falls back to built-in offline sample data.

### `_from_fbref()` method
```python
url = "https://fbref.com/en/comps/9/Premier-League-Stats"
r = requests.get(url, headers=HEADERS, timeout=15)
r.raise_for_status()
```
- Sends an HTTP GET request to fbref.com.
- `headers=HEADERS` – Sends browser-like headers to avoid being blocked.
- `timeout=15` – Waits max 15 seconds for a response.
- `raise_for_status()` – Raises an error if the server returns 4xx/5xx HTTP error.

```python
tables = pd.read_html(r.text, flavor="lxml")
df = tables[0].copy()
```
- `pd.read_html()` – Scans the HTML and extracts all `<table>` tags as DataFrames.
- `tables[0]` – We take the first table (the main standings table).
- `.copy()` – Make an independent copy to avoid modifying the original.

```python
df.columns = [c[1] if isinstance(c, tuple) else c for c in df.columns]
```
- fbref uses multi-level column headers (tuples like `("Unnamed", "Squad")`).
- This line extracts just the second level of the tuple to get plain column names.

```python
rename = {"Squad":"Team", "Rk":"Rank"}
df = df.rename(columns=rename)
```
Renames columns to our standardised names.

### `_from_wikipedia()` method
Similar to fbref, but scans through multiple tables on the Wikipedia page looking for one that has both "pts" and "gf" columns, then renames its columns using flexible matching.

### `_clean()` method
```python
def _clean(self, df):
    num = ["Rank","MP","W","D","L","GF","GA","GD","Pts","xG","xGA"]
    for c in num:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors="coerce")
```
Converts numerical columns to numbers. `errors="coerce"` replaces any non-numeric values with `NaN` instead of crashing.

```python
    df = df.dropna(subset=["Team","Pts"])
```
Removes rows where Team or Points are missing (such as sub-header rows scraped from the website).

```python
    df = df[~df["Team"].str.contains("Squad|Total|team", na=False, case=False)]
```
The `~` means NOT. Removes any rows where the Team name contains "Squad", "Total", or "team" — these are artefact rows from the website's HTML table structure.

### `_sample_data()` method
Returns a hard-coded DataFrame with realistic 2024-25 season mid-season data for all 20 PL teams, used when internet is unavailable.

---

## 7. ExcelExporter Class

```python
class ExcelExporter:
    PL_PURPLE = "38003C"   # Premier League purple (hex, no #)
    PL_GREEN  = "00FF85"   # Premier League green
    LIGHT_ROW = "F5F0F6"   # Light purple-white for alternating rows
    DARK_ROW  = "EAE0EB"   # Slightly darker for alternating rows
```

### `export()` method
```python
wb = Workbook()
ws = wb.active
ws.title = "PL Standings"
```
Creates a new Excel workbook and renames the default sheet.

```python
hf   = PatternFill("solid", fgColor=self.PL_PURPLE)
hfnt = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
ha   = Alignment(horizontal="center", vertical="center")
```
Defines the styling for header cells: purple fill, white bold text, centred.

```python
thin = Side(style="thin", color="D0C0D4")
brd  = Border(left=thin, right=thin, top=thin, bottom=thin)
```
Creates a thin border for all four sides of data cells.

```python
for ci, col in enumerate(cols, 1):
    cell = ws.cell(row=1, column=ci, value=col)
    cell.fill=hf; cell.font=hfnt; cell.alignment=ha
```
- `enumerate(cols, 1)` – Iterates with index starting at 1 (Excel columns are 1-indexed).
- `ws.cell(row, column, value)` – Writes to a specific cell.

**Rank colour-coding:**
```python
rank = int(row.get("Rank", ri+1))
rc = "1A73E8" if rank<=4 else "FF9500" if rank<=6 else "E53935" if rank>=18 else "38003C"
```
Champions League (blue), Europa League (orange), Relegation (red), or standard PL purple.

**Auto column widths:**
```python
mw = max(len(str(col)), *(len(str(df.iloc[r][col])) for r in range(len(df))))
ws.column_dimensions[get_column_letter(ci)].width = mw+4
```
Calculates the maximum content width in each column and sets the column width accordingly, adding 4 for padding.

**Chart sheet:**
Creates a second sheet "Points Chart", writes team names and points into it, then adds an openpyxl `BarChart` using those values.

---

## 8. PLStatsApp Class (Main Window)

```python
class PLStatsApp(tk.Tk):
```
Inherits from `tk.Tk` — this class IS the main application window itself.

### 8.1 `__init__` – Constructor

```python
self.title("⚽ Premier League 2024-25  |  Live Standings + Sort Visualizer")
self.geometry("1400x860")    # Default window size in pixels (width x height)
self.minsize(1100, 720)      # Minimum resize boundary
self.configure(bg=BG_DARK)  # Set window background colour
```

**State variables:**
```python
self.df          = pd.DataFrame()   # Full loaded dataset
self.filtered_df = pd.DataFrame()   # Dataset after search filter applied
self.data_source = "—"              # Where the data came from (string label)
self.is_loading  = False            # Prevents double-clicking Refresh
self._sort_col   = "Pts"            # Current sort column for Standings tab
self._sort_asc   = False            # Ascending=True / Descending=False
self._search_var = tk.StringVar()   # Tkinter variable bound to the search Entry
```

**Sort Visualizer state:**
```python
self._viz_sorting     = False    # Is the visualizer currently running?
self._viz_paused      = False    # Is it paused?
self._viz_gen         = None     # The active sorting generator object
self._viz_after_id    = None     # ID of the scheduled next animation frame
self._viz_comparisons = 0        # Running count of comparisons
self._viz_swaps       = 0        # Running count of swaps
self._viz_start_time  = 0        # perf_counter value when sort started
self._viz_sorted_idx  = set()    # Set of bar indices that are fully sorted
self._viz_teams       = []       # Team name order (for x-axis labels)
```

### 8.2 Title Bar

```python
def _build_titlebar(self):
    bar = tk.Frame(self, bg=ACCENT, height=58)
    bar.pack(fill="x")
    bar.pack_propagate(False)   # Prevent children from resizing the bar height
```
- `tk.Frame` – A rectangular container widget.
- `pack(fill="x")` – Stretches horizontally across the full window width.
- `pack_propagate(False)` – Locks the height at 58px.

```python
tk.Label(bar, text="⚽", font=("Segoe UI Emoji",22), fg=ACCENT2, bg=ACCENT).pack(side="left", padx=(16,4), pady=8)
```
A label showing the football emoji in a large font. `padx=(16,4)` means 16px left padding, 4px right padding.

```python
def btn(text, cmd, bg, fg="#000000"):
    b = tk.Button(bar, text=text, command=cmd, ...)
    b.pack(side="right", padx=6, pady=10); return b
```
Inner helper function to create a styled button and pack it to the right side of the title bar.

### 8.3 Tab 1 – Live Standings

#### Stat Cards (`_build_stat_cards`)
```python
cards = [
    ("🏆  LEADER",       "leader_val",  "—", TEXT_GOLD),
    ...
]
for title, attr, default, color in cards:
    card = tk.Frame(self.cards_frame, bg=BG_CARD, padx=14, pady=8)
    card.pack(side="left", padx=4, fill="y", expand=True)
    lbl = tk.Label(card, text=default, ...)
    setattr(self, attr, lbl)
```
- Creates 5 stat cards side-by-side.
- `setattr(self, attr, lbl)` – Dynamically sets `self.leader_val`, `self.goals_val` etc. so they can be updated later by `_update_stat_cards()`.

#### `_update_stat_cards()` method
```python
self.leader_val.config(text=df.loc[df["Pts"].idxmax(),"Team"])
```
- `df["Pts"].idxmax()` – Returns the **row index** of the row with the maximum Points value.
- `df.loc[...,"Team"]` – Gets the Team name at that row index.

#### Treeview Table (`_build_table`)
```python
style = ttk.Style()
style.theme_use("clam")
style.configure("PL.Treeview", background=BG_CARD, ...)
```
- `ttk.Style` – Customises widget appearance.
- `"clam"` theme is used as a base because it allows the most custom colour overrides.
- `"PL.Treeview"` is a custom style name applied to our specific Treeview widget.

```python
self.tree = ttk.Treeview(parent, columns=cols, show="headings", style="PL.Treeview")
```
- `columns=cols` – Defines the column names.
- `show="headings"` – Hides the default empty leftmost column.

```python
self.tree.tag_configure("cl",  foreground="#90CAF9", background="#0D1B35")
self.tree.tag_configure("rel", foreground="#EF9A9A", background="#1E0505")
```
Tagged rows are coloured differently. When inserting rows, we assign `tags=("cl",)` or `tags=("rel",)` to colour top-4 rows blue and bottom-3 rows red.

#### Points Chart (`_build_points_chart`)
```python
self.fig_pts = Figure(figsize=(4.2,7), facecolor=BG_PANEL)
self.ax_pts  = self.fig_pts.add_subplot(111)
self.canvas_pts = FigureCanvasTkAgg(self.fig_pts, master=parent)
self.canvas_pts.get_tk_widget().pack(fill="both", expand=True)
```
- `Figure(figsize=(4.2,7))` – A 4.2×7 inch matplotlib figure.
- `add_subplot(111)` – Adds one subplot (the `111` means 1 row, 1 column, plot #1).
- `FigureCanvasTkAgg` – Wraps the Figure so it can be embedded in Tkinter.
- `get_tk_widget()` – Returns the underlying Tkinter widget, which we then pack.

### 8.4 Tab 2 – Sort Visualizer

#### Vizualizer Sidebar (`_build_viz_sidebar`)
```python
self.viz_algo_var = tk.StringVar(value="Bubble Sort")
cb = ttk.Combobox(parent, textvariable=self.viz_algo_var, values=list(ALGORITHMS.keys()), state="readonly")
cb.bind("<<ComboboxSelected>>", lambda e: self._update_viz_complexity())
```
- `tk.StringVar` – A special tkinter variable that the Combobox reads/writes automatically.
- `state="readonly"` – User can only pick from the list, not type.
- `bind("<<ComboboxSelected>>", ...)` – Calls `_update_viz_complexity()` every time user picks a new algorithm, which updates the complexity card.

```python
self.viz_speed_var = tk.IntVar(value=60)
ttk.Scale(parent, from_=1, to=300, variable=self.viz_speed_var, orient="horizontal",
          command=lambda v: self.viz_speed_lbl.config(text=f"{int(float(v))} ms"))
```
- `ttk.Scale` – A slider widget.
- `variable=self.viz_speed_var` – Scale automatically updates this variable as it moves.
- `command=lambda v: ...` – Called every time the slider moves. `v` is the current value as a string, so we convert with `int(float(v))`.

#### `_update_viz_complexity()` method
```python
def _update_viz_complexity(self, *_):
    algo = self.viz_algo_var.get()
    best, worst, space = COMPLEXITY.get(algo, ("—","—","—"))
    if not hasattr(self, "cx_best"): return   # Safety: widget not created yet
    self.cx_best.config(text=best)
    self.cx_worst.config(text=worst)
    self.cx_space.config(text=space)
```
- `self.viz_algo_var.get()` – Reads the currently selected algorithm name.
- `COMPLEXITY.get(algo, ...)` – Looks up the tuple; provides fallback `("—","—","—")` if not found.
- `hasattr(self, "cx_best")` – Checks if the label widget exists before trying to update it (prevents AttributeError on startup).

#### `_viz_draw()` – The Chart Renderer
```python
def _viz_draw(self, values, teams, highlight, state, col_name):
    self.ax_viz.clear()       # Clear the previous frame
    self._style_viz_ax()      # Re-apply axis styling (cleared when axes clear)
    n = len(values)
    colors = []
    for i in range(n):
        if i in self._viz_sorted_idx or state=="done":
            colors.append(COL_SORTED)    # Green for sorted bars
        elif i in highlight:
            colors.append(COL_SWAP if state=="swap" else COL_COMPARE if state=="compare" else COL_SORTED)
        else:
            colors.append(COL_DEFAULT)   # Default indigo
```
Builds a colour list — one colour per bar — based on whether each bar is currently being compared, swapped, already sorted, or idle.

```python
    bars = self.ax_viz.bar(range(n), values, color=colors, edgecolor="none", width=0.85)
```
Draws the bar chart. `range(n)` gives x-positions 0,1,...,n-1. `values` are the bar heights. `color=colors` applies the per-bar colours.

```python
    self.ax_viz.set_xticklabels(teams, rotation=45, ha="right", fontsize=6.5)
```
Sets team names as x-axis labels, rotated 45° so they don't overlap.

```python
    self.fig_viz.tight_layout()
    self.canvas_viz.draw_idle()    # Redraw without blocking the event loop
```
`draw_idle()` is more efficient than `draw()` — it schedules a redraw at the next available moment instead of forcing an immediate repaint.

#### `_viz_start()` – Starting the Animation
```python
def _viz_start(self):
    if self._viz_sorting: return   # Already running, do nothing
    col = self.viz_col_var.get()
    working = self.df[["Team", col]].dropna().copy()
    self._viz_teams = working["Team"].tolist()        # Team names for labels
    values_arr = working[col].astype(float).tolist() # Actual stat values for sorting
    algo = self.viz_algo_var.get()
    self._viz_gen = ALGORITHMS[algo](values_arr)     # Create the generator
    self._viz_step(values_arr, col)                  # Start the animation loop
```

#### `_viz_step()` – The Animation Loop
```python
def _viz_step(self, original_values, col):
    if not self._viz_sorting: return
    if self._viz_paused:
        self._viz_after_id = self.after(100, lambda: self._viz_step(original_values, col))
        return
    try:
        arr, highlight, state, cmp_inc, swp_inc = next(self._viz_gen)
```
- `next(self._viz_gen)` – Gets the next animation frame from the sorting generator.
- If paused, we schedule another check in 100ms and return without advancing the sort.

```python
        delay = max(1, int(self.viz_speed_var.get()))
        self._viz_after_id = self.after(delay, lambda: self._viz_step(original_values, col))
```
- `self.after(delay, callback)` – Tkinter's way to schedule a function to run after `delay` milliseconds. This is how the animation loop works — each frame schedules the next frame.
- `max(1, ...)` – Ensures delay is always at least 1ms (never 0 which would freeze the GUI).

```python
    except StopIteration:
        self._viz_done(col)
```
When the generator is exhausted (no more yields), `next()` raises `StopIteration`, which we catch to call the done handler.

### 8.5 Data Loading & Threading

```python
def _fetch_data(self):
    if self.is_loading: return            # Prevent multiple simultaneous fetches
    self.is_loading = True
    self.refresh_btn.config(state="disabled", text="⏳  Loading…")
    self._start_spinner()
    threading.Thread(target=self._fetch_thread, daemon=True).start()
```
- Creates a daemon background thread to run `_fetch_thread`.
- `daemon=True` – Thread will be automatically killed when the main app closes.
- The GUI remains interactive while the web request runs in the background.

```python
def _fetch_thread(self):
    df, source = self._fetcher.fetch()    # Runs in background thread
    self.after(0, lambda: self._on_data_ready(df, source))
```
- `self.after(0, ...)` – Posts a callback to the **main thread's** event queue. This is essential because Tkinter widgets are NOT thread-safe — we must never update GUI from a background thread directly.

### 8.6 Sorting & Filtering (Standings)

```python
def _on_header_click(self, col):
    if self._sort_col == col: self._sort_asc = not self._sort_asc  # Toggle direction
    else: self._sort_col = col; self._sort_asc = (col=="Team")     # New col: asc for text
    self._apply_sort()
```
Clicking the same header toggles ascending/descending. Clicking a new header sorts ascending (or ascending alphabetically for Team).

```python
def _apply_sort(self):
    self.df = self.df.sort_values(col, ascending=asc, ignore_index=True)
    self.df["Rank"] = range(1, len(self.df)+1)  # Recalculate rank after sort
    self._apply_filter()
```
`sort_values()` is pandas' sorting method. `ignore_index=True` resets the integer index after sorting.

```python
def _apply_filter(self):
    query = self._search_var.get().strip().lower()
    self.filtered_df = (
        self.df[self.df["Team"].str.lower().str.contains(query)]
        if query and "Team" in self.df.columns else self.df.copy()
    )
```
- `self._search_var.get()` – Reads the search box text.
- `.str.lower().str.contains(query)` – Case-insensitive substring search in the Team column.
- If no search query, `filtered_df` is a full copy of `df`.

### 8.7 Excel Export

```python
def _export_excel(self):
    path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Workbook","*.xlsx")],
        initialfile="PL_Standings_2024_25.xlsx",
    )
    if not path: return   # User cancelled the dialog
```
Opens the OS save dialog. If user presses Cancel, `path` is an empty string and we return early.

### 8.8 Status Bar & Spinner

```python
_frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
```
Unicode Braille characters that look like a rotating spinner animation.

```python
def _spin(self):
    self.spinner_lbl.config(text=self._frames[self._fidx % len(self._frames)])
    self._fidx += 1
    self._fjob = self.after(80, self._spin)   # Schedule next frame in 80ms
```
Classic Tkinter animation loop — each call schedules the next call, creating an infinite loop until cancelled.

```python
def _stop_spinner(self):
    if self._fjob: self.after_cancel(self._fjob); self._fjob = None
    self.spinner_lbl.config(text="✔")   # Show checkmark when done
```
`after_cancel()` stops the scheduled loop.

---

## 9. Entry Point

```python
if __name__ == "__main__":
    app = PLStatsApp()
    app.mainloop()
```
- `if __name__ == "__main__":` – This block runs only when the file is executed directly (not when imported as a module).
- `PLStatsApp()` – Creates the app window (calls `__init__`, builds UI, starts data fetch).
- `app.mainloop()` – Starts the Tkinter event loop. The window stays open and responsive, processing user events (clicks, key presses, timer callbacks) until the window is closed.

---

## Summary Table – All Classes and Methods

| Class / Function | Purpose |
|---|---|
| `bubble_sort(arr)` | Bubble Sort generator |
| `selection_sort(arr)` | Selection Sort generator |
| `insertion_sort(arr)` | Insertion Sort generator |
| `merge_sort(arr)` | Merge Sort generator (calls helpers) |
| `_merge_helper(a,l,r)` | Recursive divide step for Merge Sort |
| `_merge(a,l,mid,r)` | Merge two sorted halves |
| `quick_sort(arr)` | Quick Sort generator |
| `_quick_helper(a,low,high)` | Recursive Quick Sort |
| `_partition(a,low,high)` | Partition step for Quick Sort |
| `heap_sort(arr)` | Heap Sort generator |
| `_heapify(a,n,i)` | Fix heap property at node i |
| `DataFetcher.fetch()` | Try all sources, return best data |
| `DataFetcher._from_fbref()` | Scrape from fbref.com |
| `DataFetcher._from_wikipedia()` | Scrape from Wikipedia |
| `DataFetcher._clean()` | Clean and validate DataFrame |
| `DataFetcher._sample_data()` | Return hard-coded offline data |
| `ExcelExporter.export()` | Write formatted Excel file |
| `PLStatsApp.__init__()` | Initialize state, build UI, start fetch |
| `PLStatsApp._build_titlebar()` | Purple PL title bar with buttons |
| `PLStatsApp._build_standings_tab()` | Tab 1 layout |
| `PLStatsApp._build_stat_cards()` | 5 stat summary cards |
| `PLStatsApp._update_stat_cards()` | Refresh card values from data |
| `PLStatsApp._build_table()` | Sortable Treeview standings table |
| `PLStatsApp._build_points_chart()` | Horizontal bar chart (right panel) |
| `PLStatsApp._update_points_chart()` | Redraw chart with current data |
| `PLStatsApp._build_viz_tab()` | Tab 2 layout |
| `PLStatsApp._build_viz_sidebar()` | Controls panel for Sort Visualizer |
| `PLStatsApp._update_viz_complexity()` | Update complexity card on algo change |
| `PLStatsApp._build_viz_chart()` | Matplotlib chart for Sort Visualizer |
| `PLStatsApp._viz_draw()` | Render one animation frame |
| `PLStatsApp._viz_start()` | Begin sort animation |
| `PLStatsApp._viz_step()` | Advance one generator frame |
| `PLStatsApp._viz_done()` | Handle sort completion |
| `PLStatsApp._viz_toggle_pause()` | Pause or resume animation |
| `PLStatsApp._viz_reset()` | Stop and clear the visualizer |
| `PLStatsApp._fetch_data()` | Start background data fetch |
| `PLStatsApp._fetch_thread()` | Background thread target |
| `PLStatsApp._on_data_ready()` | Handle data on main thread |
| `PLStatsApp._on_header_click()` | Sort table by clicked column |
| `PLStatsApp._apply_sort()` | Sort the DataFrame |
| `PLStatsApp._apply_filter()` | Filter by search query |
| `PLStatsApp._refresh_table()` | Repopulate Treeview rows |
| `PLStatsApp._export_excel()` | Save dialog + call exporter |
| `PLStatsApp._build_statusbar()` | Bottom status bar |
| `PLStatsApp._start_spinner()` | Begin spinner animation |
| `PLStatsApp._spin()` | Spinner animation frame |
| `PLStatsApp._stop_spinner()` | Stop spinner, show ✔ |

---

*End of Documentation — pl_stats_app.py*
