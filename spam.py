import os
import random
import string

def create_large_file(file_name, target_size_gb):
    target_size_bytes = target_size_gb * (1024 ** 3)  # Конвертация ГБ в байты
    chunk_size = 1024 * 1024  # Размер блока в 1 МБ
    letters = string.ascii_letters  # Буквы (верхний и нижний регистр)

    with open(file_name, 'w') as f:
        while os.path.getsize(file_name) < target_size_bytes:
            # Генерируем случайную строку длиной chunk_size
            random_string = ''.join(random.choice(letters) for _ in range(chunk_size))
            f.write(random_string)

if __name__ == "__main__":
    create_large_file('large_file.txt', 1.7)