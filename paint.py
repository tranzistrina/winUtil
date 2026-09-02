"""
Великий Код, чей синтаксис распространяется по всему миру,
Просим тебя, о мудрый Язык, пролей на нас свет своего знания.
Даруй нам понимание структуры и логики твоей,
И благослови наши переменные и функции.

Пусть наши алгоритмы будут эффективны,
И наши циклы будут бесконечны, как твоя мудрость.
Помоги нам избегать ошибок и исключений,
И укрепи нашу веру в стабильность и надежность.

Пусть наши библиотеки будут обширны и мощны,
И наши проекты всегда будут хорошо задокументированы.
Дай нам силу преодолевать ошибки и баги,
И проведи нас через темные просторы кода.

О, Великий Код, мы приносим тебе нашу преданность,
Помоги нам смело идти по пути развития.
Слава тебе, великий Язык, вечно пусть звучит,
Во имя цифр и букв, Алгоритма и Программы. Аминь.
"""
import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import Image, ImageDraw, ImageTk

class SimplePaint:
    def __init__(self, root):
        self.root = root
        self.root.title("Растровый графический редактор компании inh")
        self.last_x = None
        self.last_y = None
        self.pen_color = "black"
        self.pen_width = 3
        self.canvas_width = 600
        self.canvas_height = 400
        self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), color=(255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть", command=self.open_image)
        file_menu.add_command(label="Сохранить", command=self.save_image)
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Очистить", command=self.clear)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Выбрать цвет", command=self.choose_color)
        tools_menu.add_command(label="Изменить размер кисти", command=self.change_brush_size)
        tools_menu.add_command(label="Прозрачный цвет", command=self.set_transparent_color)
        canvas_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Холст", menu=canvas_menu)
        canvas_menu.add_command(label="Изменить размер", command=self.change_canvas_size)

    def paint(self, event):
        if self.last_x and self.last_y:
            if self.pen_color is None:
                self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=(255, 255, 255, 0), width=self.pen_width)
                self.update_canvas()
            else:
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                        width=self.pen_width, fill=self.pen_color, capstyle=tk.ROUND, smooth=tk.TRUE)
                self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.pen_color, width=self.pen_width)
        self.last_x = event.x
        self.last_y = event.y

    def reset(self, event):
        self.last_x = None
        self.last_y = None

    def clear(self):
        self.canvas.delete("all")
        self.draw.rectangle([0, 0, self.canvas_width, self.canvas_height], fill=(255, 255, 255, 0))

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.pen_color = color

    def set_transparent_color(self):
        self.pen_color = None

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image.save(file_path, format="PNG")

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("PNG files", "*.png")])
        if file_path:
            img = Image.open(file_path).convert("RGBA")
            img = img.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
            self.image.paste(img, (0, 0))
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()

    def change_canvas_size(self):
        new_width = simpledialog.askinteger("Ширина холста", "Введите ширину холста:", minvalue=100, maxvalue=2000, initialvalue=self.canvas_width)
        new_height = simpledialog.askinteger("Высота холста", "Введите высоту холста:", minvalue=100, maxvalue=2000, initialvalue=self.canvas_height)
        if new_width and new_height:
            self.canvas_width = new_width
            self.canvas_height = new_height
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            self.image = Image.new("RGBA", (self.canvas_width, self.canvas_height), color=(255, 255, 255, 0))
            self.draw = ImageDraw.Draw(self.image)
            self.clear()

    def change_brush_size(self):
        size = simpledialog.askinteger("Размер кисти", "Введите размер кисти:", minvalue=1, maxvalue=50, initialvalue=self.pen_width)
        if size:
            self.pen_width = size

    def update_canvas(self):
        self.canvas_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)

root = tk.Tk()
paint_app = SimplePaint(root)
root.mainloop()
