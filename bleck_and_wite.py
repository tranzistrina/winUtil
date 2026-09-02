import os
from PIL import Image

def convert_to_bw(input_image_path, output_image_path):
    color_image = Image.open(input_image_path)
    bw_image = color_image.convert("L")  # Конвертируем изображение в черно-белый формат
    bw_image.save(output_image_path)

if __name__ == "__main__":
    input_dir = "."  # Директория, где находятся исходные изображения
    output_dir = "bw_images"  # Директория для сохранения черно-белых изображений

    # Создаем директорию для сохранения черно-белых изображений, если она не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Обрабатываем каждый файл с расширением .png в директории input_dir
    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            convert_to_bw(input_path, output_path)