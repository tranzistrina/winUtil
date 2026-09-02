#!/usr/bin/env python3
"""
P2P локальный чат + групповая аудиоконференция через Multicast UDP.
- Не требует аккаунтов и централизованного сервера.
- Для обнаружения и обмена используется Multicast (239.255.0.1).
- Чат и аудио идут по разным портам.
- Компиляция в .exe: pyinstaller --noconsole --onefile p2p_multicast_chat_audio.py

Зависимости: python 3.8+, sounddevice, numpy
pip install sounddevice numpy

Примечание: multicast работает в локальной сети (LAN). Не требует проброса портов на роутере.
"""

import socket
import struct
import threading
import json
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sounddevice as sd
import numpy as np
import pathlib
import sys

MCAST_GRP = '239.255.0.1'
CHAT_PORT = 50000
AUDIO_PORT = 50001
TTL = 1

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
DTYPE = 'int16'

recv_chat_q = queue.Queue()
recv_audio_q = queue.Queue()
running = True

def get_local_ips():
    ips = set()
    try:
        hostname = socket.gethostname()
        for res in socket.getaddrinfo(hostname, None):
            ips.add(res[4][0])
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    return ips

LOCAL_IPS = get_local_ips()

def create_mcast_receiver(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('', port))
    except OSError:
        sock.bind((MCAST_GRP, port))
    mreq = struct.pack('4s4s', socket.inet_aton(MCAST_GRP), socket.inet_aton('0.0.0.0'))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def create_mcast_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl_bin = struct.pack('b', TTL)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    return sock

def chat_listener(app_nick):
    sock = create_mcast_receiver(CHAT_PORT)
    while running:
        try:
            data, addr = sock.recvfrom(65536)
            if not data:
                continue
            try:
                obj = json.loads(data.decode('utf-8'))
                nick = obj.get('nick')
                msg = obj.get('msg')
            except Exception:
                continue
            if addr[0] in LOCAL_IPS and nick == app_nick:
                continue
            recv_chat_q.put((nick, msg, addr[0]))
        except Exception:
            continue

def audio_listener(my_port=0):
    sock = create_mcast_receiver(AUDIO_PORT)
    while running:
        try:
            data, addr = sock.recvfrom(65536)
            if not data:
                continue
            if addr[0] in LOCAL_IPS:
                continue
            recv_audio_q.put(data)
        except Exception:
            continue

def chat_sender(nick, message):
    sock = create_mcast_sender()
    payload = json.dumps({'nick': nick, 'msg': message}).encode('utf-8')
    sock.sendto(payload, (MCAST_GRP, CHAT_PORT))
    sock.close()

class AudioStreamer(threading.Thread):
    def __init__(self, nick):
        super().__init__(daemon=True)
        self.nick = nick
        self.running = False
        self.sock = create_mcast_sender()

    def run(self):
        self.running = True
        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, blocksize=CHUNK) as stream:
                while self.running:
                    data, _ = stream.read(CHUNK)
                    raw = data.tobytes()
                    try:
                        self.sock.sendto(raw, (MCAST_GRP, AUDIO_PORT))
                    except Exception:
                        pass
        except Exception:
            pass

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass

class AudioPlayer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.running = True
        self.stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, blocksize=CHUNK)
        self.stream.start()

    def run(self):
        while self.running:
            try:
                data = recv_audio_q.get()
                if data is None:
                    continue
                arr = np.frombuffer(data, dtype=np.int16)
                try:
                    arr = arr.reshape(-1, CHANNELS)
                except Exception:
                    continue
                try:
                    self.stream.write(arr)
                except Exception:
                    pass
            except Exception:
                continue

    def stop(self):
        self.running = False
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass

class P2PApp:
    def __init__(self, root):
        self.root = root
        root.title('Локальный P2P чат + голос (Multicast)')
        self.nick_var = tk.StringVar(value=f'User{socket.gethostname()[:6]}')

        top = tk.Frame(root)
        top.pack(fill='x')
        tk.Label(top, text='Ник:').pack(side='left')
        self.nick_entry = tk.Entry(top, textvariable=self.nick_var)
        self.nick_entry.pack(side='left', padx=5)

        self.chat_area = ScrolledText(root, state='disabled', width=60, height=20)
        self.chat_area.pack(padx=5, pady=5)

        bottom = tk.Frame(root)
        bottom.pack(fill='x')

        self.msg_var = tk.StringVar()
        self.msg_entry = tk.Entry(bottom, textvariable=self.msg_var)
        self.msg_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.msg_entry.bind('<Return>', lambda e: self.send_chat())

        send_btn = tk.Button(bottom, text='Отправить', command=self.send_chat)
        send_btn.pack(side='left', padx=5)

        self.audio_btn = tk.Button(root, text='Включить микрофон', command=self.toggle_audio)
        self.audio_btn.pack(pady=4)

        self.status_label = tk.Label(root, text='Готово', anchor='w')
        self.status_label.pack(fill='x')

        self.chat_thread = None
        self.audio_recv_thread = None
        self.audio_player = None
        self.audio_streamer = None

        self.start_listeners()
        self.root.after(200, self.process_incoming)

    def start_listeners(self):
        nick = self.nick_var.get()
        self.chat_thread = threading.Thread(target=chat_listener, args=(nick,), daemon=True)
        self.chat_thread.start()
        self.audio_recv_thread = threading.Thread(target=audio_listener, daemon=True)
        self.audio_recv_thread.start()
        self.audio_player = AudioPlayer()
        self.audio_player.start()

    def send_chat(self):
        nick = self.nick_var.get().strip() or 'Anon'
        msg = self.msg_var.get().strip()
        if not msg:
            return
        try:
            chat_sender(nick, msg)
            self.append_chat(nick, msg, 'me')
            self.msg_var.set('')
        except Exception as e:
            self.append_system(f'Ошибка при отправке: {e}')

    def append_chat(self, nick, msg, addr):
        self.chat_area.config(state='normal')
        if addr == 'me':
            self.chat_area.insert('end', f'Я ({nick}): {msg}\n')
        else:
            self.chat_area.insert('end', f'{nick}@{addr}: {msg}\n')
        self.chat_area.see('end')
        self.chat_area.config(state='disabled')

    def append_system(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert('end', f'[SYSTEM] {text}\n')
        self.chat_area.see('end')
        self.chat_area.config(state='disabled')

    def toggle_audio(self):
        if self.audio_streamer and self.audio_streamer.running:
            self.audio_streamer.stop()
            self.audio_streamer = None
            self.audio_btn.config(text='Включить микрофон')
            self.status_label.config(text='Микрофон выключен')
        else:
            try:
                nick = self.nick_var.get().strip() or 'Anon'
                self.audio_streamer = AudioStreamer(nick)
                self.audio_streamer.start()
                self.audio_btn.config(text='Выключить микрофон')
                self.status_label.config(text='Микрофон включен')
            except Exception as e:
                self.append_system(f'Не удалось включить микрофон: {e}')

    def process_incoming(self):
        while not recv_chat_q.empty():
            nick, msg, addr = recv_chat_q.get()
            self.append_chat(nick, msg, addr)

        self.root.after(200, self.process_incoming)

if __name__ == '__main__':
    root = tk.Tk()
    app = P2PApp(root)
    root.mainloop()
