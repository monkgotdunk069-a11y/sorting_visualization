import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

class DSAVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Sorting Visualizer (Pos/Neg/Zero)")
        self.root.geometry("1000x700")
        self.root.config(bg="#121212")

        self.array = []
        self.original_array = []
        self.is_sorting = False
        self.start_time = 0
        self.setup_ui()

    def setup_ui(self):
        # --- Control Panel ---
        self.ctrl_frame = tk.Frame(self.root, bg="#1e1e1e", pady=10)
        self.ctrl_frame.pack(fill="x")

        tk.Label(self.ctrl_frame, text="Input Array:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
        self.user_input = tk.Entry(self.ctrl_frame, width=30)
        self.user_input.insert(0, "10, -25, 0, 45, -10, 30, -5")
        self.user_input.grid(row=0, column=1, padx=5)

        tk.Button(self.ctrl_frame, text="Load", command=self.load_data, bg="#3498db", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(self.ctrl_frame, text="Randomize", command=self.generate_random, bg="#9b59b6", fg="white").grid(row=0, column=3, padx=5)

        self.algo_menu = ttk.Combobox(self.ctrl_frame, values=["Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort", "Quick Sort", "Heap Sort"])
        self.algo_menu.grid(row=0, column=4, padx=5)
        self.algo_menu.current(0)

        tk.Button(self.ctrl_frame, text="SORT", command=self.start_sorting, bg="#2ecc71", fg="white", width=10).grid(row=0, column=5, padx=10)

        self.time_label = tk.Label(self.ctrl_frame, text="Time: 0.00 seconds", fg="white", bg="#1e1e1e")
        self.time_label.grid(row=0, column=6, padx=10)

        tk.Button(self.ctrl_frame, text="Compare All", command=self.compare_all, bg="#e74c3c", fg="white").grid(row=0, column=7, padx=5)

        # --- Canvas ---
        self.canvas = tk.Canvas(self.root, width=900, height=500, bg="#121212", highlightthickness=0)
        self.canvas.pack(pady=20)

    def load_data(self):
        try:
            self.array = [int(x.strip()) for x in self.user_input.get().split(",")]
            self.original_array = self.array.copy()
            self.draw_array(self.array, ["#5dade2"] * len(self.array))
        except:
            messagebox.showerror("Error", "Use format: 10, -5, 0, 20")

    def generate_random(self):
        self.array = [random.randint(-50, 50) for _ in range(15)]
        self.original_array = self.array.copy()
        self.draw_array(self.array, ["#5dade2"] * len(self.array))

    def draw_array(self, data, color_list):
        self.canvas.delete("all")
        if not data: return

        c_height, c_width = 500, 900
        x_width = c_width / len(data)
        
        # Calculate dynamic scaling based on absolute max value
        max_val = max([abs(x) for x in data]) if data else 1
        if max_val == 0: max_val = 1
        
        # The 'Zero Line' is in the vertical center of the canvas
        zero_y = c_height / 2
        scale = (c_height / 2.2) / max_val

        # Draw the Zero Baseline
        self.canvas.create_line(0, zero_y, c_width, zero_y, fill="#444", width=2)

        for i, val in enumerate(data):
            x0 = i * x_width + 5
            x1 = (i + 1) * x_width - 5
            
            # Bar height calculation
            y_val = zero_y - (val * scale)
            
            # Draw Bar (Negative bars go down from zero_y, Positive go up)
            self.canvas.create_rectangle(x0, zero_y, x1, y_val, fill=color_list[i], outline="white")
            
            # Draw Value Text
            text_pos = y_val - 12 if val >= 0 else y_val + 12
            self.canvas.create_text((x0 + x1)/2, text_pos, text=str(val), fill="white", font=("Arial", 9, "bold"))
        
        self.root.update()

    # --- Sorting Logic ---
    def start_sorting(self):
        if self.is_sorting: return
        self.is_sorting = True
        self.start_time = time.time()
        algo = self.algo_menu.get()

        if algo == "Bubble Sort": gen = self.bubble_sort()
        elif algo == "Insertion Sort": gen = self.insertion_sort()
        elif algo == "Selection Sort": gen = self.selection_sort()
        elif algo == "Merge Sort": gen = self.merge_sort(0, len(self.array)-1)
        elif algo == "Quick Sort": gen = self.quick_sort(0, len(self.array)-1)
        elif algo == "Heap Sort": gen = self.heap_sort()

        self.animate(gen)

    def animate(self, gen):
        try:
            next(gen)
            self.root.after(100, lambda: self.animate(gen))
        except StopIteration:
            elapsed_time = time.time() - self.start_time
            self.time_label.config(text=f"Time: {elapsed_time:.2f} seconds")
            self.draw_array(self.array, ["#2ecc71"] * len(self.array))
            self.is_sorting = False

    def bubble_sort(self):
        n = len(self.array)
        for i in range(n):
            for j in range(0, n - i - 1):
                if self.array[j] > self.array[j + 1]:
                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    self.draw_array(self.array, ["#e74c3c" if x == j or x == j+1 else "#5dade2" for x in range(n)])
                    yield

    def selection_sort(self):
        for i in range(len(self.array)):
            min_idx = i
            for j in range(i+1, len(self.array)):
                if self.array[j] < self.array[min_idx]: min_idx = j
                self.draw_array(self.array, ["#e74c3c" if x == j or x == min_idx else "#5dade2" for x in range(len(self.array))])
                yield
            self.array[i], self.array[min_idx] = self.array[min_idx], self.array[i]

    def insertion_sort(self):
        for i in range(1, len(self.array)):
            key = self.array[i]
            j = i - 1
            while j >= 0 and key < self.array[j]:
                self.array[j + 1] = self.array[j]
                j -= 1
                self.draw_array(self.array, ["#e74c3c" if x == j else "#5dade2" for x in range(len(self.array))])
                yield
            self.array[j + 1] = key

    def merge_sort(self, l, r):
        if l < r:
            m = (l + r) // 2
            yield from self.merge_sort(l, m)
            yield from self.merge_sort(m + 1, r)
            
            left, right = self.array[l:m+1], self.array[m+1:r+1]
            i = j = 0
            for k in range(l, r + 1):
                if i < len(left) and (j >= len(right) or left[i] <= right[j]):
                    self.array[k] = left[i]; i += 1
                else:
                    self.array[k] = right[j]; j += 1
                self.draw_array(self.array, ["#f1c40f" if l <= x <= r else "#5dade2" for x in range(len(self.array))])
                yield

    def quick_sort(self, low, high):
        if low < high:
            pivot = self.array[high]
            i = low - 1
            for j in range(low, high):
                if self.array[j] < pivot:
                    i += 1
                    self.array[i], self.array[j] = self.array[j], self.array[i]
                self.draw_array(self.array, ["#e67e22" if x == high else "#5dade2" for x in range(len(self.array))])
                yield
            self.array[i+1], self.array[high] = self.array[high], self.array[i+1]
            p = i + 1
            yield from self.quick_sort(low, p - 1)
            yield from self.quick_sort(p + 1, high)

    def heap_sort(self):
        n = len(self.array)
        for i in range(n // 2 - 1, -1, -1):
            yield from self.heapify(n, i)
        for i in range(n-1, 0, -1):
            self.array[i], self.array[0] = self.array[0], self.array[i]
            yield from self.heapify(i, 0)

    def heapify(self, n, i):
        largest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and self.array[l] > self.array[largest]: largest = l
        if r < n and self.array[r] > self.array[largest]: largest = r
        if largest != i:
            self.array[i], self.array[largest] = self.array[largest], self.array[i]
            self.draw_array(self.array, ["#f1c40f" if x == i or x == largest else "#5dade2" for x in range(len(self.array))])
            yield
            yield from self.heapify(n, largest)

    def compare_all(self):
        if not self.original_array:
            messagebox.showerror("Error", "Please load or generate an array first.")
            return

        algorithms = ["Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort", "Quick Sort", "Heap Sort"]
        times = {}

        for algo in algorithms:
            self.array = self.original_array.copy()
            start_time = time.time()

            if algo == "Bubble Sort":
                for _ in self.bubble_sort(): pass
            elif algo == "Insertion Sort":
                for _ in self.insertion_sort(): pass
            elif algo == "Selection Sort":
                for _ in self.selection_sort(): pass
            elif algo == "Merge Sort":
                for _ in self.merge_sort(0, len(self.array)-1): pass
            elif algo == "Quick Sort":
                for _ in self.quick_sort(0, len(self.array)-1): pass
            elif algo == "Heap Sort":
                for _ in self.heap_sort(): pass

            elapsed_time = time.time() - start_time
            times[algo] = elapsed_time

        # Display comparison in a messagebox
        comparison_text = "Algorithm Comparison:\n\n"
        for algo, t in times.items():
            comparison_text += f"{algo}: {t:.4f} seconds\n"
        messagebox.showinfo("Comparison Results", comparison_text)

        # Reset to original array
        self.array = self.original_array.copy()
        self.draw_array(self.array, ["#5dade2"] * len(self.array))

if __name__ == "__main__":
    root = tk.Tk()
    app = DSAVisualizer(root)
    root.mainloop()
