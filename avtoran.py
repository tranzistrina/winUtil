import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import random
import json

# Определяем путь к папке с установщиками и файл конфигурации
installers_folder = "progi"
config_file = "installers_config.json"

# Функция для генерации случайного числа от 1 до 5
def generate_random_number():
    return random.randint(1, 255)

# Функция для создания конфигурационного файла с именами установщиков
def create_config_file():
    installers = [f for f in os.listdir(installers_folder) if f.endswith('.exe')]
    config_data = {}

    for installer in installers:
        display_name = f"{installer.split('.')[0]}-{generate_random_number()}.exe"
        config_data[installer] = display_name

    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    return config_data

# Проверяем наличие конфигурационного файла, создаем если его нет
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config_data = json.load(f)
else:
    if not os.path.exists(installers_folder):
        messagebox.showerror("Ошибка", f"Папка '{installers_folder}' не найдена.")
        exit()
    config_data = create_config_file()

# Функция для запуска установщика
def run_installer(installer):
    installer_path = os.path.join(installers_folder, installer)
    try:
        subprocess.Popen(installer_path, shell=True)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить {installer}: {e}")

# Создаем главное окно
root = tk.Tk()
root.title("Установщики")

# Создаем список установщиков и кнопок
for installer, display_name in config_data.items():
    frame = tk.Frame(root)
    frame.pack(fill='x', padx=5, pady=5)

    label = tk.Label(frame, text=display_name)
    label.pack(side='left', padx=5)

    install_button = tk.Button(frame, text="Install", command=lambda i=installer: run_installer(i))
    install_button.pack(side='right', padx=5)

# Запускаем главное окно
root.mainloop()
