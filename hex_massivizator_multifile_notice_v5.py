import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import json
import binascii

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to ChipProg Converter")
        self.root.geometry("600x450")
        self.images = []
        self.image_paths = []
        self.dither = tk.BooleanVar(value=False)
        self.resize_option = tk.StringVar(value="resize")
        self.output_format = tk.StringVar(value="Binary image (*.bin)")
        self.formats = [
            "Binary image (*.bin)",
            "Motorola S-record (*.srec)",
            "Extended Intel HEX (*.hex)",
            "TI-TXT (*.txt)",
            "ASCII Hex (*.hex)",
            "JSON (*.json)"
        ]
        self.create_widgets()

    def create_widgets(self):
        self.img_label = tk.Label(self.root, text="Выберите изображения", width=60, height=4)
        self.img_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        self.load_button = tk.Button(self.root, text="Загрузить изображения", command=self.load_images)
        self.load_button.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        self.convert_button = tk.Button(self.root, text="Преобразовать", command=self.convert_images)
        self.convert_button.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
        options_frame = tk.LabelFrame(self.root, text="Параметры преобразования")
        options_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        self.dither_checkbox = tk.Checkbutton(options_frame, text="Использовать дизеринг", variable=self.dither)
        self.dither_checkbox.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        resize_label = tk.Label(options_frame, text="Режим изменения размера:")
        resize_label.grid(row=0, column=1, padx=5, pady=2, sticky="e")
        self.resize_option_menu = ttk.Combobox(options_frame, textvariable=self.resize_option,
                                               values=["resize", "fill"], state="readonly", width=8)
        self.resize_option_menu.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        format_label = tk.Label(options_frame, text="Формат вывода:")
        format_label.grid(row=1, column=1, padx=5, pady=2, sticky="e")
        self.format_menu = ttk.Combobox(options_frame, textvariable=self.output_format,
                                        values=self.formats, state="readonly", width=25)
        self.format_menu.grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.status_label = tk.Label(self.root, text="Загрузите изображения",
                                     width=60, height=2, anchor="w", justify=tk.LEFT)
        self.status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    def load_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Выберите изображения",
            filetypes=[("Image files", "*.jpg;*.png;*.jpeg")]
        )
        if file_paths:
            self.images = []
            self.image_paths = list(file_paths)
            for path in self.image_paths:
                try:
                    image = Image.open(path)
                    self.images.append(image)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{path}\n\n{e}")
            if self.images:
                self.display_image(self.images[0])
                self.status_label.config(text=f"Загружено изображений: {len(self.images)}")

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
                error = old_pixel - new_pixel
                if x + 1 < img.width:
                    pixels[y, x + 1] += error * 7 / 16
                if x > 0 and y + 1 < img.height:
                    pixels[y + 1, x - 1] += error * 3 / 16
                if y + 1 < img.height:
                    pixels[y + 1, x] += error * 5 / 16
                if x + 1 < img.width and y + 1 < img.height:
                    pixels[y + 1, x + 1] += error * 1 / 16
        pixels = np.clip(pixels, 0, 255)
        return Image.fromarray(pixels)

    def convert_images(self):
        if not self.images:
            messagebox.showerror("Ошибка", "Сначала загрузите изображения")
            return
        byte_array_all = bytearray()
        for img in self.images:
            img_proc = img.resize((192, 144)) if self.resize_option.get() == "resize" else Image.new("RGB", (192, 144))
            if self.resize_option.get() == "fill":
                img_proc.paste(img, (0, 0))
            if self.dither.get():
                img_proc = self.dithering(img_proc)
            img_proc = img_proc.convert('1')
            pixels = np.array(img_proc)
            for row in pixels:
                s = ''.join(['1' if pixel > 0 else '0' for pixel in row])
                for i in range(0, 192, 8):
                    byte_array_all.append(int(s[i:i+8], 2))
        notice = "Development of the inh team. It is not subject to copying.              "
        notice_bytes = bytearray(notice.encode("ascii"))
        byte_array_all = notice_bytes + byte_array_all
        format_name = self.output_format.get()
        content = ""
        file_ext = ".bin"
        if "Binary" in format_name:
            content = byte_array_all
            file_ext = ".bin"
        elif "JSON" in format_name:
            content = json.dumps({
                "width": 192,
                "height": 144,
                "frames": len(self.images),
                "notice": notice,
                "data": list(byte_array_all)
            }, indent=2)
            file_ext = ".json"
        else:
            content = binascii.hexlify(byte_array_all).decode("ascii")
            file_ext = ".hex"
        output_path = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            filetypes=[(f"{format_name}", f"*{file_ext}"), ("All files", "*.*")]
        )
        if output_path:
            try:
                if "Binary" in format_name:
                    with open(output_path, "wb") as f:
                        f.write(content)
                else:
                    with open(output_path, "w") as f:
                        f.write(content)
                self.status_label.config(text=f"Файл сохранён: {output_path}")
                messagebox.showinfo("Готово", f"Файл сохранён: {output_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

def main():
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
