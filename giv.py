import os
from PIL import Image

def create_gif(image_list, gif_name, duration):
    frames = []
    for image_name in image_list:
        im = Image.open(image_name)
        frames.append(im)

    frames[0].save(gif_name, save_all=True, append_images=frames[1:], optimize=False, duration=duration, loop=0)

def main():
    # Получаем список всех файлов PNG в текущей директории
    png_files = [f for f in os.listdir() if f.endswith('.png')]

    # Читаем задержку из файла "частота.txt"
    with open('частота.txt', 'r') as f:
        delay = int(f.read().strip())

    # Создаем GIF
    create_gif(png_files, 'output.gif', duration=delay)

if __name__ == "__main__":
    main()