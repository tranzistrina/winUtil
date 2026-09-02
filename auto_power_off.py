import tkinter as tk
import os
import time
import ctypes

TIMER_DURATION = 3 * 60 * 60  # 3 часа (в секундах)

start_time = None

def disable_close_button(window):
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    hMenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
    ctypes.windll.user32.RemoveMenu(hMenu, 0xF060, 0x00000000)

def schedule_shutdown(seconds):
    # Запускаем отложенное выключение сразу
    os.system(f"shutdown /s /t {seconds}")

def update_timer():
    if start_time is None:
        return
    elapsed = int(time.time() - start_time)
    remaining = TIMER_DURATION - elapsed
    if remaining <= 0:
        countdown_label.config(text="Выключение...")
    else:
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        secs = remaining % 60
        countdown_label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
        root.after(1000, update_timer)

def start_timer():
    global start_time
    start_time = time.time()
    # Сразу запускаем отложенное выключение на 3 часа
    schedule_shutdown(TIMER_DURATION)
    start_button.pack_forget()
    label.config(text="До выключения осталось:")
    update_timer()

# Создание интерфейса
root = tk.Tk()
root.title("Аренда сервера")
root.geometry("300x180")
root.resizable(False, False)

label = tk.Label(root, text="Нажмите кнопку для запуска аренды", font=("Arial", 12))
label.pack(pady=10)

countdown_label = tk.Label(root, text="", font=("Arial", 24))
countdown_label.pack(pady=10)

start_button = tk.Button(root, text="Начать", font=("Arial", 14), command=start_timer)
start_button.pack()

disable_close_button(root)

root.mainloop()
