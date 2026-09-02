import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

class ImageConverterApp:
    def __init__(self, root):
        self.root=root; self.root.title('Image to ChipProg Converter'); self.root.geometry('600x450')
        self.img=None; self.dither=tk.BooleanVar(value=False); self.resize_option=tk.StringVar(value='resize'); self.output_format=tk.StringVar(value='Binary image (*.bin)')
        self.formats=['Binary image (*.bin)','Motorola S-record (*.srec)','Extended Intel HEX (*.hex)','TI-TXT (*.txt)','ASCII Hex (*.hex)','JSON (*.json)']; self.create_widgets()
    def create_widgets(self):
        self.img_label=tk.Label(self.root,text='Выберите изображение для преобразования',width=60,height=4); self.img_label.grid(row=0,column=0,columnspan=2,padx=10,pady=5)
        tk.Button(self.root,text='Загрузить изображение',command=self.load_image).grid(row=1,column=0,pady=5,padx=10,sticky='ew'); tk.Button(self.root,text='Преобразовать',command=self.convert_image).grid(row=1,column=1,pady=5,padx=10,sticky='ew')
        frame=tk.LabelFrame(self.root,text='Параметры преобразования'); frame.grid(row=2,column=0,columnspan=2,padx=10,pady=5,sticky='ew')
        tk.Checkbutton(frame,text='Использовать дизеринг',variable=self.dither).grid(row=0,column=0,padx=5,pady=2,sticky='w')
        tk.Label(frame,text='Режим размера:').grid(row=0,column=1,padx=5); ttk.Combobox(frame,textvariable=self.resize_option,values=['resize','fill'],state='readonly',width=8).grid(row=0,column=2,padx=5)
        tk.Label(frame,text='Формат:').grid(row=1,column=1,padx=5); ttk.Combobox(frame,textvariable=self.output_format,values=self.formats,state='readonly',width=25).grid(row=1,column=2,padx=5)
        self.status=tk.Label(self.root,text='Выберите изображение',width=60,height=2,anchor='w'); self.status.grid(row=3,column=0,columnspan=2,padx=10,pady=5,sticky='w')
    def load_image(self):
        p=filedialog.askopenfilename(filetypes=[('Image files','*.jpg;*.png;*.jpeg')])
        if p: self.img=Image.open(p); self.status.config(text=f'Изображение загружено: {p}'); self.display_image(self.img)
    def display_image(self,img):
        preview=img.copy(); preview.thumbnail((200,200)); self.img_label.config(image=ImageTk.PhotoImage(preview),text=''); self.img_label.image=self.img_label.cget('image')
    def dithering(self,img):
        a=np.array(img.convert('L'),dtype=float)
        for y in range(a.shape[0]-1):
            for x in range(a.shape[1]-1):
                old=a[y,x]; new=255 if old>127 else 0; a[y,x]=new; e=old-new; a[y,x+1]+=e*7/16; a[y+1,x-1]+=e*3/16 if x else 0; a[y+1,x]+=e*5/16; a[y+1,x+1]+=e/16
        return Image.fromarray(np.clip(a,0,255).astype('uint8'))
    def intel_hex(self,data):
        out=[]
        for address in range(0,len(data),16):
            chunk=data[address:address+16]; rec=[len(chunk),(address>>8)&255,address&255,0]+list(chunk); checksum=(-sum(rec))&255; out.append(':'+''.join(f'{x:02X}' for x in rec+[checksum]))
        out.append(':00000001FF'); return '\n'.join(out)
    def convert_image(self):
        if not self.img: messagebox.showerror('Ошибка','Загрузите изображение'); return
        if self.resize_option.get()=='resize': img=self.img.resize((192,144))
        else:
            img=Image.new('RGB',(192,144),'black'); img.paste(self.img,(0,0))
        if self.dither.get(): img=self.dithering(img)
        a=np.array(img.convert('1')); data=bytearray()
        for row in a:
            bits=''.join('1' if p else '0' for p in row); data.extend(int(bits[i:i+8],2) for i in range(0,192,8))
        fmt=self.output_format.get(); ext='.bin'
        if 'Intel HEX' in fmt: content=self.intel_hex(data); ext='.hex'; mode='w'
        elif 'ASCII Hex' in fmt: content=data.hex(); ext='.hex'; mode='w'
        elif 'JSON' in fmt:
            import json; content=json.dumps({'width':192,'height':144,'data':list(data)},indent=2); ext='.json'; mode='w'
        else: content=data; mode='wb'
        out=filedialog.asksaveasfilename(defaultextension=ext)
        if out:
            with open(out,mode) as f: f.write(content)
            self.status.config(text=f'Сохранено: {out}')

if __name__=='__main__':
    root=tk.Tk(); ImageConverterApp(root); root.mainloop()
