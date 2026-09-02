import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Array Converter")
        self.root.geometry("600x400")
        self.img = None
        self.image_path = ""
        self.dither = tk.BooleanVar(value=False)
        self.resize_option = tk.StringVar(value="resize")
        self.create_widgets()

    def create_widgets(self):
        self.img_label = tk.Label(self.root, text="Выберите изображение для преобразования", width=60, height=4)
        self.img_label.grid(row=0, column=0, columnspan=2)
        self.load_button = tk.Button(self.root, text="Загрузить изображение", command=self.load_image)
        self.load_button.grid(row=1, column=0, pady=10)
        self.convert_button = tk.Button(self.root, text="Преобразовать", command=self.convert_image)
        self.convert_button.grid(row=1, column=1, pady=10)
        self.dither_checkbox = tk.Checkbutton(self.root, text="Использовать дизеринг", variable=self.dither)
        self.dither_checkbox.grid(row=2, column=0, columnspan=2)
        self.resize_option_menu = tk.OptionMenu(self.root, self.resize_option, "resize", "fill")
        self.resize_option_menu.grid(row=3, column=0, columnspan=2)
        self.status_label = tk.Label(self.root, text="Выберите изображение и настройте параметры", width=60, height=2)
        self.status_label.grid(row=4, column=0, columnspan=2)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
        if file_path:
            self.image_path = file_path
            self.img = Image.open(self.image_path)
            self.display_image(self.img)
            self.status_label.config(text=f"Изображение загружено: {self.image_path}")

    def display_image(self, img):
        img.thumbnail((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        self.img_label.config(image=img_tk, text="")
        self.img_label.image = img_tk

    def dithering(self, img):
        img = img.convert("L")
        pixels = np.array(img)
        for y in range(img.height - 1):
            for x in range(img.width - 1):
                old_pixel = pixels[y, x]
                new_pixel = 255 if old_pixel > 127 else 0
                pixels[y, x] = new_pixel
                quant_error = old_pixel - new_pixel
                if x + 1 < img.width:
                    pixels[y, x + 1] += quant_error * 7 / 16
                if x - 1 >= 0 and y + 1 < img.height:
                    pixels[y + 1, x - 1] += quant_error * 3 / 16
                if y + 1 < img.height:
                    pixels[y + 1, x] += quant_error * 5 / 16
                if x + 1 < img.width and y + 1 < img.height:
                    pixels[y + 1, x + 1] += quant_error * 1 / 16
        pixels = np.clip(pixels, 0, 255)
        return Image.fromarray(pixels)

    def convert_image(self):
        if not self.img:
            messagebox.showerror("Ошибка", "Пожалуйста, загрузите изображение!")
            return
        resize_mode = self.resize_option.get()
        if resize_mode == "resize":
            img_resized = self.img.resize((192, 144))
        else:
            img_resized = Image.new("RGB", (192, 144), color="black")
            img_resized.paste(self.img, (0, 0))
        if self.dither.get():
            img_resized = self.dithering(img_resized)
        img_resized = img_resized.convert('1')
        pixels = np.array(img_resized)
        pixel_array = []
        for row in pixels:
            pixel_array.append("  { " + ", ".join(str(int(pixel)) for pixel in row) + " },")
        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if output_path:
            with open(output_path, "w") as file:
                file.write("\n".join(pixel_array))
            self.status_label.config(text=f"Массив сохранён в файл {output_path}")
            messagebox.showinfo("Готово", f"Массив успешно сохранён в {output_path}")

def main():
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
