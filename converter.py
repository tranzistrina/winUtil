import os
from PIL import Image

# Словарь с поддерживаемыми форматами
supported_formats = {
    'jpg': 'JPEG',
    'png': 'PNG',
    'iso': 'ISO',
    'pdf': 'PDF',
    'svg': 'SVG',
    'webp': 'WEBP'
}

# Функция для конвертирования файлов
def convert_files(input_dir, output_dir, extensions):
    for filename in os.listdir(input_dir):
        if filename.endswith(tuple(extensions)):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.' + extensions[1])
            try:
                with Image.open(input_path) as img:
                    img.save(output_path, format=extensions[1])
            except Exception as e:
                print(f"Ошибка при конвертации файла {filename}: {e}")

# Функция для чтения списка расширений из файла
def read_extensions_from_file(file_path):
    with open(file_path, 'r') as file:
        extensions = file.read().split()
    return extensions

if __name__ == "__main__":
    # Директория с исходными файлами
    input_directory = '.'  # Можно изменить на путь к вашей директории

    # Директория для сохранения конвертированных файлов
    output_directory = 'converted_files'  # Можно изменить на путь к вашей директории

    # Создание директории для сохранения конвертированных файлов, если её нет
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Чтение списка расширений из файла
    extensions_file = 'расширения.txt'  # Имя файла со списком расширений
    extensions = read_extensions_from_file(extensions_file)

    # Конвертирование файлов
    convert_files(input_directory, output_directory, extensions)

    print("Конвертация завершена.")