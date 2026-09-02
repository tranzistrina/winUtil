import tkinter as tk
from tkinter import filedialog,messagebox
from tkinter.scrolledtext import ScrolledText
import os

class TextEditor:
    def __init__(self,root):
        self.root=root; self.root.title('Текстовый редактор'); self.path=None
        self.text=ScrolledText(root,wrap='word',undo=True); self.text.pack(fill='both',expand=True)
        bar=tk.Frame(root); bar.pack(fill='x')
        for title,cmd in [('Новый',self.new),('Открыть',self.open),('Сохранить',self.save),('Сохранить как',self.save_as)]: tk.Button(bar,text=title,command=cmd).pack(side='left',padx=3,pady=3)
        tk.Label(bar,text='  Ctrl+S для сохранения').pack(side='left')
        self.root.bind('<Control-s>',lambda e:self.save())
        self.root.protocol('WM_DELETE_WINDOW',self.close)
    def new(self):
        if self.text.get('1.0','end-1c') and not messagebox.askyesno('Новый','Очистить текущий документ?'): return
        self.text.delete('1.0','end'); self.path=None
    def open(self):
        p=filedialog.askopenfilename(filetypes=[('Text/Python','*.txt;*.py;*.json;*.md'),('All files','*.*')])
        if p:
            with open(p,'r',encoding='utf-8') as f: data=f.read()
            self.text.delete('1.0','end'); self.text.insert('1.0',data); self.path=p
    def save(self): return self.save_as() if not self.path else self._write(self.path)
    def save_as(self):
        p=filedialog.asksaveasfilename(defaultextension='.txt',filetypes=[('Text files','*.txt'),('All files','*.*')])
        if p:self.path=p; return self._write(p)
    def _write(self,p):
        with open(p,'w',encoding='utf-8') as f:f.write(self.text.get('1.0','end-1c'))
        self.root.title(f'Текстовый редактор - {os.path.basename(p)}')
    def close(self): self.root.destroy()

if __name__=='__main__':
    root=tk.Tk(); TextEditor(root); root.mainloop()
