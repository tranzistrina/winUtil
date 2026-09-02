import tkinter as tk
from tkinter import filedialog, messagebox

class TextComparer:
    def __init__(self, root):
        self.root = root
        self.root.title("Сравнение текстов")
        self.text1 = tk.Text(root, width=60, height=20, wrap="word")
        self.text2 = tk.Text(root, width=60, height=20, wrap="word")
        self.text1.grid(row=0, column=0, padx=5, pady=5)
        self.text2.grid(row=0, column=1, padx=5, pady=5)
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text="Загрузить текст 1", command=lambda: self.load_text(self.text1)).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Загрузить текст 2", command=lambda: self.load_text(self.text2)).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Сравнить", command=self.compare_texts).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="◀ Предыдущее", command=lambda: self.navigate(-1)).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Следующее ▶", command=lambda: self.navigate(1)).grid(row=0, column=4, padx=5)
        self.text1.tag_config("diff", background="red", foreground="white")
        self.text2.tag_config("diff", background="red", foreground="white")
        self.differences = []
        self.current_index = -1

    def load_text(self, text_widget):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", content)

    def compare_texts(self):
        self.text1.tag_remove("diff", "1.0", tk.END)
        self.text2.tag_remove("diff", "1.0", tk.END)
        self.differences.clear()
        self.current_index = -1
        t1 = self.text1.get("1.0", tk.END).rstrip("\n")
        t2 = self.text2.get("1.0", tk.END).rstrip("\n")
        max_len = max(len(t1), len(t2))
        for i in range(max_len):
            c1 = t1[i] if i < len(t1) else ""
            c2 = t2[i] if i < len(t2) else ""
            if c1 != c2:
                if i < len(t1):
                    index1 = f"1.0+{i}c"
                    self.text1.tag_add("diff", index1, f"{index1}+1c")
                    self.differences.append((self.text1, index1))
                if i < len(t2):
                    index2 = f"1.0+{i}c"
                    self.text2.tag_add("diff", index2, f"{index2}+1c")
                    self.differences.append((self.text2, index2))
        if not self.differences:
            messagebox.showinfo("Результат", "Тексты идентичны!")

    def navigate(self, direction):
        if not self.differences:
            return
        self.current_index = (self.current_index + direction) % len(self.differences)
        widget, index = self.differences[self.current_index]
        widget.see(index)
        widget.mark_set("insert", index)
        widget.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextComparer(root)
    root.mainloop()
