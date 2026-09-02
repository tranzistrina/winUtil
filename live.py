import tkinter as tk
from tkinter import filedialog
import random
import threading
import time
import os
import mss
from PIL import Image

def create_random_field(rows, cols):
    return [[random.randint(0, 1) for _ in range(cols)] for _ in range(rows)]

def next_generation(field, rows, cols):
    new_field = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            neighbors = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    rr = (r + dr) % rows
                    cc = (c + dc) % cols
                    neighbors += field[rr][cc]
            if field[r][c] == 1 and neighbors in (2, 3):
                new_field[r][c] = 1
            elif field[r][c] == 0 and neighbors == 3:
                new_field[r][c] = 1
    return new_field

def draw_field(canvas, field, cell_size):
    canvas.delete("all")
    rows = len(field)
    cols = len(field[0])
    for r in range(rows):
        for c in range(cols):
            if field[r][c] == 1:
                x1 = c * cell_size
                y1 = r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")

def take_screenshot(path, index):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.rgb)
        img.save(f"{path}/igra_{index}.png")

def run_life(params, canvas):
    rows = params["rows"]
    cols = params["cols"]
    cell = params["cell"]
    delay = params["delay"]
    ticks_before_regen = params["ticks"]
    screenshot_enabled = params["scr"]
    save_folder = params["folder"]
    screenshot_index = 1
    tick = 0
    field = create_random_field(rows, cols)
    while params["running_flag"][0]:
        draw_field(canvas, field, cell)
        if screenshot_enabled:
            take_screenshot(save_folder, screenshot_index)
            screenshot_index += 1
        field = next_generation(field, rows, cols)
        tick += 1
        if tick >= ticks_before_regen:
            field = create_random_field(rows, cols)
            tick = 0
        time.sleep(delay)

def start_game():
    rows = int(row_var.get())
    cols = int(col_var.get())
    cell = int(cell_var.get())
    width = cols * cell
    height = rows * cell
    vis = tk.Toplevel(root)
    vis.title("Игра Жизнь — визуализация")
    canvas = tk.Canvas(vis, width=width, height=height, bg="white")
    canvas.pack()
    params = {
        "rows": rows,
        "cols": cols,
        "cell": cell,
        "delay": float(delay_var.get()),
        "ticks": int(ticks_var.get()),
        "folder": folder_var.get(),
        "scr": screenshot_var.get(),
        "running_flag": [True],
    }
    thread = threading.Thread(target=run_life, args=(params, canvas), daemon=True)
    thread.start()

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

root = tk.Tk()
root.title("Игра Жизнь — настройки")
row_var = tk.StringVar(value="50")
col_var = tk.StringVar(value="50")
cell_var = tk.StringVar(value="10")
delay_var = tk.StringVar(value="0.5")
ticks_var = tk.StringVar(value="50")
folder_var = tk.StringVar(value=os.getcwd())
screenshot_var = tk.BooleanVar(value=True)
labels = [
    ("Строк", row_var),
    ("Столбцов", col_var),
    ("Размер клетки (px)", cell_var),
    ("Задержка между шагами (сек)", delay_var),
    ("Шагов до перегенерации поля", ticks_var),
]
for label, var in labels:
    tk.Label(root, text=label).pack()
    tk.Entry(root, textvariable=var).pack()
tk.Label(root, text="Папка сохранения скриншотов").pack()
tk.Entry(root, textvariable=folder_var, width=40).pack()
tk.Button(root, text="Выбрать...", command=choose_folder).pack()
tk.Checkbutton(root, text="Делать скриншоты", variable=screenshot_var).pack()
tk.Button(root, text="Запустить", command=start_game, bg="green", fg="white").pack(pady=10)
root.mainloop()
