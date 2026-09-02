import tkinter as tk
from tkinter import filedialog
import os
import threading
import pygame

class MusicPlayer:
    def __init__(self,root):
        self.root=root; self.root.title('Музыкальный проигрыватель'); self.root.geometry('500x350'); pygame.mixer.init(); self.files=[]; self.current=-1
        self.listbox=tk.Listbox(root); self.listbox.pack(fill='both',expand=True,padx=10,pady=10)
        controls=tk.Frame(root); controls.pack()
        for text,cmd in [('Добавить',self.add),('▶',self.play),('⏸',self.pause),('⏹',self.stop),('Следующий',self.next)]: tk.Button(controls,text=text,command=cmd).pack(side='left',padx=3)
    def add(self):
        paths=filedialog.askopenfilenames(filetypes=[('Audio','*.mp3;*.wav;*.ogg;*.flac')])
        for p in paths: self.files.append(p); self.listbox.insert('end',os.path.basename(p))
    def play(self):
        sel=self.listbox.curselection()
        if sel:self.current=sel[0]
        if 0<=self.current<len(self.files): pygame.mixer.music.load(self.files[self.current]); pygame.mixer.music.play()
    def pause(self): pygame.mixer.music.pause()
    def stop(self): pygame.mixer.music.stop()
    def next(self):
        if self.files: self.current=(self.current+1)%len(self.files); self.listbox.selection_clear(0,'end'); self.listbox.selection_set(self.current); self.play()

if __name__=='__main__':
    root=tk.Tk(); MusicPlayer(root); root.mainloop()
