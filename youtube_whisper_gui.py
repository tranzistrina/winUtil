import os, re, threading, traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
from faster_whisper import WhisperModel

def safe_filename(name: str) -> str:
    name=re.sub(r'[<>:"/\\|?*\x00-\x1F]','_',name); return name.strip('. ') or 'youtube_audio'

def format_time(seconds: float) -> str:
    ms=int((seconds-int(seconds))*1000); s=int(seconds)%60; m=(int(seconds)//60)%60; h=int(seconds)//3600
    return f'{h:02d}:{m:02d}:{s:02d}.{ms:03d}'

class YouTubeWhisperApp:
    def __init__(self,root):
        self.root=root; root.title('YouTube → Whisper → TXT'); root.geometry('820x620')
        self.url_var=tk.StringVar(); self.folder_var=tk.StringVar(value=str(Path.home()/'Desktop'))
        self.model_var=tk.StringVar(value='small'); self.device_var=tk.StringVar(value='cpu'); self.compute_var=tk.StringVar(value='int8'); self.language_var=tk.StringVar(); self.timestamps_var=tk.BooleanVar(value=True); self.is_running=False
        main=ttk.Frame(root); main.pack(fill='both',expand=True,padx=12,pady=12)
        ttk.Label(main,text='Ссылка на YouTube:').grid(row=0,column=0,sticky='w',padx=10,pady=6); ttk.Entry(main,textvariable=self.url_var).grid(row=0,column=1,columnspan=2,sticky='ew',padx=10,pady=6)
        ttk.Label(main,text='Папка результата:').grid(row=1,column=0,sticky='w',padx=10,pady=6); ttk.Entry(main,textvariable=self.folder_var).grid(row=1,column=1,sticky='ew',padx=10,pady=6); ttk.Button(main,text='Выбрать',command=self.choose_folder).grid(row=1,column=2,padx=10,pady=6)
        ttk.Label(main,text='Модель:').grid(row=2,column=0,sticky='w',padx=10,pady=6); ttk.Combobox(main,textvariable=self.model_var,state='readonly',values=['tiny','base','small','medium','large-v3','turbo','distil-large-v3']).grid(row=2,column=1,sticky='ew',padx=10,pady=6)
        ttk.Label(main,text='Устройство:').grid(row=3,column=0,sticky='w',padx=10,pady=6); ttk.Combobox(main,textvariable=self.device_var,state='readonly',values=['cpu','cuda']).grid(row=3,column=1,sticky='ew',padx=10,pady=6)
        ttk.Label(main,text='Compute type:').grid(row=4,column=0,sticky='w',padx=10,pady=6); ttk.Combobox(main,textvariable=self.compute_var,state='readonly',values=['int8','float32','float16','int8_float16']).grid(row=4,column=1,sticky='ew',padx=10,pady=6)
        ttk.Label(main,text='Язык:').grid(row=5,column=0,sticky='w',padx=10,pady=6); ttk.Entry(main,textvariable=self.language_var).grid(row=5,column=1,sticky='ew',padx=10,pady=6)
        ttk.Checkbutton(main,text='Добавлять таймкоды',variable=self.timestamps_var).grid(row=6,column=1,sticky='w',padx=10,pady=6)
        self.start_button=ttk.Button(main,text='Скачать и распознать',command=self.start_process); self.start_button.grid(row=7,column=0,columnspan=3,sticky='ew',padx=10,pady=12)
        self.progress=ttk.Progressbar(main,mode='indeterminate'); self.progress.grid(row=8,column=0,columnspan=3,sticky='ew',padx=10,pady=6)
        ttk.Label(main,text='Лог:').grid(row=9,column=0,sticky='w',padx=10,pady=6); self.log_text=tk.Text(main,height=14,wrap='word'); self.log_text.grid(row=10,column=0,columnspan=3,sticky='nsew',padx=10,pady=6)
        main.columnconfigure(1,weight=1); main.rowconfigure(10,weight=1)
    def choose_folder(self):
        folder=filedialog.askdirectory();
        if folder:self.folder_var.set(folder)
    def log(self,msg): self.root.after(0,lambda:(self.log_text.insert('end',msg+'\n'),self.log_text.see('end')))
    def set_running(self,r):
        self.is_running=r
        if r:self.start_button.config(state='disabled'); self.progress.start(10)
        else:self.start_button.config(state='normal'); self.progress.stop()
    def start_process(self):
        if self.is_running:return
        url=self.url_var.get().strip(); out=self.folder_var.get().strip()
        if not url:return messagebox.showerror('Ошибка','Вставьте ссылку на YouTube.')
        if not out:return messagebox.showerror('Ошибка','Выберите папку для результата.')
        Path(out).mkdir(parents=True,exist_ok=True)
        settings={'url':url,'out_dir':out,'model_size':self.model_var.get(),'device':self.device_var.get(),'compute_type':self.compute_var.get(),'language':self.language_var.get().strip() or None,'timestamps':self.timestamps_var.get()}
        threading.Thread(target=self.worker,args=(settings,),daemon=True).start()
    def download_audio(self,url,out_dir):
        self.log('Скачиваю аудиодорожку...'); downloaded={'path':None}
        def hook(d):
            if d.get('status')=='finished': downloaded['path']=d.get('filename'); self.log('Загрузка завершена.')
        opts={'format':'bestaudio/best','outtmpl':str(Path(out_dir)/'%(title).150B.%(ext)s'),'noplaylist':True,'quiet':True,'no_warnings':True,'progress_hooks':[hook]}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url,download=True); info=info['entries'][0] if 'entries' in info else info; title=info.get('title','youtube_audio'); path=downloaded['path'] or ydl.prepare_filename(info)
        if not Path(path).exists(): raise FileNotFoundError('Не удалось найти скачанный файл.')
        return path,title
    def transcribe_to_txt(self,audio_path,title,out_dir,model_size,device,compute_type,language,timestamps):
        out=Path(out_dir)/ (safe_filename(title)+'.txt'); i=2
        while out.exists(): out=Path(out_dir)/f'{safe_filename(title)}_{i}.txt'; i+=1
        model=WhisperModel(model_size,device=device,compute_type=compute_type); segments,info=model.transcribe(audio_path,beam_size=5,language=language,vad_filter=True)
        with open(out,'w',encoding='utf-8') as f:
            f.write(f'Источник: {title}\nЯзык: {getattr(info,"language","unknown")}\n\n')
            for s in segments:
                t=s.text.strip()
                if t:f.write((f'[{format_time(s.start)} --> {format_time(s.end)}] ' if timestamps else '')+t+'\n'); self.log(t)
        return out
    def worker(self,settings):
        self.set_running(True)
        try:
            audio,title=self.download_audio(settings['url'],settings['out_dir']); out=self.transcribe_to_txt(audio,title,settings['out_dir'],settings['model_size'],settings['device'],settings['compute_type'],settings['language'],settings['timestamps']); self.root.after(0,lambda:messagebox.showinfo('Готово',f'Расшифровка сохранена:\n{out}'))
        except Exception as e:self.log(traceback.format_exc()); self.root.after(0,lambda:messagebox.showerror('Ошибка',str(e)))
        finally:self.set_running(False)

if __name__=='__main__':
    root=tk.Tk(); YouTubeWhisperApp(root); root.mainloop()
