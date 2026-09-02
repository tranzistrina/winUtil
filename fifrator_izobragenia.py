import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox

ASCII_CHARS = "abcdefghijklmnopqrstuvwxyz"[:16]
COLOR_PALETTE = [
    (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
    (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
    (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
    (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)
]
CHAR_TO_COLOR = {char: COLOR_PALETTE[i] for i, char in enumerate(ASCII_CHARS)}

def resize_image(image, new_width=100, aspect_ratio=1.0):
    width, height = image.size
    ratio = height / width / aspect_ratio
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def adjust_contrast(image, factor):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def find_closest_color(pixel, palette):
    return min(range(len(palette)), key=lambda i: np.linalg.norm(np.array(palette[i]) - np.array(pixel)))

def pixel_to_ascii(image):
    pixels = np.array(image)
    ascii_str = ""
    for pixel_row in tqdm(pixels, desc="Конвертация пикселей в ASCII", unit="строка"):
        for pixel in pixel_row:
            closest_color_index = find_closest_color(pixel, COLOR_PALETTE)
            ascii_str += ASCII_CHARS[closest_color_index]
        ascii_str += "-"
    return ascii_str

def image_to_ascii(image_path, output_path, width=100, contrast=1.0, aspect_ratio=1.0):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(e)
        return
    image = resize_image(image, width, aspect_ratio)
    image = adjust_contrast(image, contrast)
    ascii_str = f"Ширина: {width}, Контраст: {contrast}, Соотношение сторон: {aspect_ratio}\n"
    ascii_str += pixel_to_ascii(image)
    with open(output_path, "w") as f:
        f.write(ascii_str)
    print(f"ASCII арт сохранен в {output_path}")

def create_image_from_text(input_path, output_path, mode='text'):
    with open(input_path, 'r', encoding='utf-8') as file:
        text = file.read()
    lines = text.split('-')
    height = len(lines)
    width = max(len(line) for line in lines)
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for y, line in enumerate(tqdm(lines, desc="Рисование текста", unit="строка")):
        for x, char in enumerate(line):
            color = CHAR_TO_COLOR.get(char, (255, 255, 255))
            if mode == 'text':
                draw.text((x, y), char, fill=color)
            else:
                image.putpixel((x, y), color)
    image.save(output_path)

def select_input_file():
    input_file.set(filedialog.askopenfilename())

def select_output_file():
    output_file.set(filedialog.asksaveasfilename(defaultextension=".txt"))

def swap_paths():
    input_path = input_file.get()
    output_path = output_file.get()
    input_file.set(output_path)
    output_file.set(input_path)

def generate_ascii_art():
    if not input_file.get() or not output_file.get():
        messagebox.showerror("Ошибка", "Необходимо указать пути к файлам")
        return
    try:
        width = int(width_entry.get() or 100)
        contrast = float(contrast_entry.get() or 1.0)
        aspect_ratio = float(aspect_ratio_entry.get() or 1.0)
        image_to_ascii(input_file.get(), output_file.get(), width, contrast, aspect_ratio)
        messagebox.showinfo("Готово", "ASCII арт успешно создан!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

def create_image_from_ascii_text():
    if not input_file.get() or not output_file.get():
        messagebox.showerror("Ошибка", "Необходимо указать пути к файлам")
        return
    try:
        mode = mode_var.get()
        create_image_from_text(input_file.get(), output_file.get(), mode)
        messagebox.showinfo("Готово", "Изображение успешно создано!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

root = tk.Tk()
root.title("ASCII Art Generator")
input_file = tk.StringVar()
output_file = tk.StringVar()

tk.Label(root, text="Путь к входному файлу:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Entry(root, textvariable=input_file, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Выбрать", command=select_input_file).grid(row=0, column=2, padx=10, pady=10)
tk.Label(root, text="Путь к выходному файлу:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
tk.Entry(root, textvariable=output_file, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Выбрать", command=select_output_file).grid(row=1, column=2, padx=10, pady=10)
tk.Button(root, text="Поменять местами", command=swap_paths).grid(row=1, column=3, padx=10, pady=10)
tk.Label(root, text="Ширина (по умолчанию 100):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
width_entry = tk.Entry(root); width_entry.grid(row=2, column=1, padx=10, pady=10)
tk.Label(root, text="Контраст (по умолчанию 1.0):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
contrast_entry = tk.Entry(root); contrast_entry.grid(row=3, column=1, padx=10, pady=10)
tk.Label(root, text="Соотношение сторон (по умолчанию 1.0):").grid(row=4, column=0, padx=10, pady=10, sticky="e")
aspect_ratio_entry = tk.Entry(root); aspect_ratio_entry.grid(row=4, column=1, padx=10, pady=10)
tk.Button(root, text="Создать ASCII арт", command=generate_ascii_art).grid(row=5, column=0, columnspan=3, padx=10, pady=10)
tk.Label(root, text="Режим вывода:").grid(row=6, column=0, padx=10, pady=10, sticky="e")
mode_var = tk.StringVar(value='text')
tk.Radiobutton(root, text="Текст", variable=mode_var, value='text').grid(row=6, column=1, padx=10, pady=10, sticky="w")
tk.Radiobutton(root, text="Пиксели", variable=mode_var, value='pixel').grid(row=6, column=1, padx=10, pady=10, sticky="e")
tk.Button(root, text="Создать изображение из текста", command=create_image_from_ascii_text).grid(row=7, column=0, columnspan=3, padx=10, pady=10)
root.mainloop()
