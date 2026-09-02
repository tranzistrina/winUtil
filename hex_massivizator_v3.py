import tkinter as tk
from tkinter import filedialog,messagebox
from PIL import Image
import numpy as np

def image_to_bytes(path,size=(192,144)):
    img=Image.open(path).convert('L').resize(size)
    a=np.array(img)
    data=bytearray()
    for row in a:
        bits=''.join('1' if p>=128 else '0' for p in row)
        data.extend(int(bits[i:i+8],2) for i in range(0,size[0],8))
    return data

def intel_hex(data):
    lines=[]
    for addr in range(0,len(data),16):
        chunk=list(data[addr:addr+16]); rec=[len(chunk),(addr>>8)&255,addr&255,0]+chunk; lines.append(':'+''.join(f'{x:02X}' for x in rec+[(-sum(rec))&255]))
    return '\n'.join(lines+[':00000001FF'])

def main():
    root=tk.Tk(); root.withdraw(); path=filedialog.askopenfilename(filetypes=[('Images','*.png;*.jpg;*.jpeg')])
    if not path:return
    data=image_to_bytes(path); out=filedialog.asksaveasfilename(defaultextension='.hex',filetypes=[('Intel HEX','*.hex'),('Binary','*.bin')])
    if out:
        if out.lower().endswith('.bin'): open(out,'wb').write(data)
        else: open(out,'w',encoding='ascii').write(intel_hex(data))
        messagebox.showinfo('Готово',f'Файл сохранён: {out}')
if __name__=='__main__': main()
