import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import pandas as pd

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

        # User name field
        tk.Label(self.ctrl_frame, text="User Name:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
        self.user_name = tk.Entry(self.ctrl_frame, width=20)
        self.user_name.insert(0, "Nishant")  # default
        self.user_name.grid(row=0, column=1, padx=5)

        # Array input field
        tk.Label(self.ctrl_frame, text="Input Array:", fg="white", bg="#1e1e1e").grid(row=0, column=2, padx=5)
        self.user_input = tk.Entry(self.ctrl_frame, width=30)
        self.user_input.insert(0, "10, -25, 0, 45, -10, 30, -5")
        self.user_input.grid(row=0, column=3, padx=5)

        tk.Button(self.ctrl_frame, text="Load", command=self.load_data, bg="#3498db", fg="white").grid(row=0, column=4, padx=5)
        tk.Button(self.ctrl_frame, text="Randomize", command=self.generate_random, bg="#9b59b6", fg="white").grid(row=0, column=5, padx=5)

        self.algo_menu = ttk.Combobox(self.ctrl_frame, values=["Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort", "Quick Sort", "Heap Sort"])
        self.algo_menu.grid(row=0, column=6, padx=5)
        self.algo_menu.current(0)

        tk.Button(self.ctrl_frame, text="SORT", command=self.start_sorting, bg="#2ecc71", fg="white", width=10).grid(row=0, column=7, padx=10)

        self.time_label = tk.Label(self.ctrl_frame, text="Time: 0.00 seconds", fg="white", bg="#1e1e1e")
        self.time_label.grid(row=0, column=8, padx=10)

        tk.Button(self.ctrl_frame, text="Compare All", command=self.compare_all, bg="#e74c3c", fg="white").grid(row=0, column=9, padx=5)

        # Save to Excel button
        tk.Button(self.ctrl_frame, text="Save to Excel", command=self.save_to_excel, bg="#f39c12", fg="white").grid(row=0, column=10, padx=5)

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
        
        max_val = max([abs(x) for x in data]) if data else 1
        if max_val == 0: max_val = 1
        
        zero_y = c_height / 2
        scale = (c_height / 2.2) / max_val

        self.canvas.create_line(0, zero_y, c_width, zero_y, fill="#444", width=2)

        for i, val in enumerate(data):
            x0 = i * x_width + 5
            x1 = (i + 1) * x_width - 5
            y_val = zero_y - (val * scale)
            self.canvas.create_rectangle(x0, zero_y, x1, y_val, fill=color_list[i], outline="white")
            text_pos = y_val - 12 if val >= 0 else y_val + 12
            self.canvas.create_text((x0 + x1)/2, text_pos, text=str(val), fill="white", font=("Arial", 9, "bold"))
        
        self.root.update()

    # --- Sorting Logic (same as your code) ---
    # [Bubble, Selection, Insertion, Merge, Quick, Heap sort methods unchanged]

    def save_to_excel(self):
        if not self.array:
            messagebox.showerror("Error", "No array loaded to save.")
            return

        username = self.user_name.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a user name.")
            return

        # Create DataFrame
        df = pd.DataFrame({
            "User": [username] * len(self.array),
            "Values": self.array
        })

        # Append or create Excel file
        try:
            existing_df = pd.read_excel("sorting_data.xlsx")
            final_df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            final_df = df

        final_df.to_excel("sorting_data.xlsx", index=False)
        messagebox.showinfo("Saved", f"Data saved for {username} in sorting_data.xlsx")

if __name__ == "__main__":
    root = tk.Tk()
    app = DSAVisualizer(root)
    root.mainloop()