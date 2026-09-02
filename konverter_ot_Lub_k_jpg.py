import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from PIL import Image

class ImageToJpgConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер изображений в JPG")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.input_dir = tk.StringVar()
        self.overwrite = tk.BooleanVar(value=False)
        self.quality = tk.IntVar(value=85)
        self.conversion_running = False
        self.create_widgets()

    def create_widgets(self):
        frame_dir = tk.Frame(self.root)
        frame_dir.pack(pady=10, padx=10, fill=tk.X)
        tk.Label(frame_dir, text="Папка с изображениями:").pack(side=tk.LEFT)
        tk.Entry(frame_dir, textvariable=self.input_dir, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(frame_dir, text="Обзор...", command=self.select_directory).pack(side=tk.RIGHT)
        frame_settings = tk.Frame(self.root)
        frame_settings.pack(pady=10, padx=10, fill=tk.X)
        tk.Checkbutton(frame_settings, text="Перезаписывать существующие JPG-файлы", variable=self.overwrite).pack(anchor=tk.W)
        tk.Label(frame_settings, text="Качество JPG (1-100):").pack(anchor=tk.W)
        tk.Scale(frame_settings, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.quality, length=300).pack(anchor=tk.W, pady=5)
        self.btn_convert = tk.Button(self.root, text="НАЧАТЬ КОНВЕРТАЦИЮ", command=self.start_conversion, font=("Arial", 10, "bold"))
        self.btn_convert.pack(pady=10)
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.pack(pady=10, padx=10, fill=tk.X)
        tk.Label(self.root, text="Лог конвертации:").pack(anchor=tk.W, padx=10)
        self.log_area = scrolledtext.ScrolledText(self.root, height=15, state=tk.DISABLED)
        self.log_area.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.status_var = tk.StringVar(value="Готов")
        tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.set(directory)

    def log_message(self, message, level="INFO"):
        def _log():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, f"{message}\n")
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
        self.root.after(0, _log)

    def update_progress(self, value, maximum):
        def _update():
            self.progress['maximum'] = maximum
            self.progress['value'] = value
        self.root.after(0, _update)

    def update_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def finish_conversion(self, success, message):
        self.conversion_running = False
        self.btn_convert.config(state=tk.NORMAL)
        if success:
            self.update_status("Конвертация завершена")
            messagebox.showinfo("Готово", message)
        else:
            self.update_status("Ошибка конвертации")
            messagebox.showerror("Ошибка", message)

    def convert_images(self):
        directory = self.input_dir.get().strip()
        if not directory:
            self.finish_conversion(False, "Пожалуйста, выберите папку.")
            return
        if not os.path.isdir(directory):
            self.finish_conversion(False, "Указанная папка не существует.")
            return
        extensions = ('.png', '.bmp', '.tiff', '.tif', '.webp', '.gif', '.ico', '.jpeg', '.jpg')
        files = [f for f in os.listdir(directory) if f.lower().endswith(extensions)]
        if not files:
            self.finish_conversion(False, "В выбранной папке нет поддерживаемых изображений.")
            return
        total = len(files)
        converted = skipped = errors = 0
        self.log_message(f"Найдено файлов: {total}")
        self.update_progress(0, total)
        for idx, filename in enumerate(files):
            if not self.conversion_running:
                break
            input_path = os.path.join(directory, filename)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(directory, name + ".jpg")
            if ext.lower() in ('.jpg', '.jpeg') and not self.overwrite.get():
                self.log_message(f"Пропуск (уже JPG): {filename}")
                skipped += 1
                self.update_progress(idx + 1, total)
                continue
            if os.path.exists(output_path) and not self.overwrite.get():
                self.log_message(f"Пропуск (файл {output_path} существует, перезапись отключена)")
                skipped += 1
                self.update_progress(idx + 1, total)
                continue
            try:
                with Image.open(input_path) as img:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(output_path, 'JPEG', quality=self.quality.get())
                    self.log_message(f"Конвертирован: {filename} -> {name}.jpg")
                    converted += 1
            except Exception as e:
                self.log_message(f"ОШИБКА при конвертации {filename}: {str(e)}", level="ERROR")
                errors += 1
            self.update_progress(idx + 1, total)
        result_msg = f"Конвертация завершена.\n✅ Успешно: {converted}\n⏭️ Пропущено: {skipped}\n❌ Ошибок: {errors}\nВсего обработано: {total}"
        self.finish_conversion(True, result_msg)
        self.log_message(result_msg)

    def start_conversion(self):
        if self.conversion_running:
            messagebox.showwarning("Внимание", "Конвертация уже выполняется.")
            return
        self.conversion_running = True
        self.btn_convert.config(state=tk.DISABLED)
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.update_status("Конвертация запущена...")
        threading.Thread(target=self.convert_images, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToJpgConverter(root)
    root.mainloop()
