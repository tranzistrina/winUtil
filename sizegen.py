import random

def generate_random_text(length):
    # Генерируем случайные символы кроме пробела и новой строки
    characters = [chr(i) for i in range(33, 127) if i != 32 and i != 10]
    random_text = ''.join(random.choice(characters) for _ in range(length))
    return random_text

def create_file(output_filename, output_size):
    with open(output_filename, 'w') as f:
        # Генерируем текст нужного размера
        while output_size > 0:
            # Генерируем блоки текста размером от 1 до 1000 символов
            block_size = min(output_size, random.randint(1, 1000))
            random_text = generate_random_text(block_size)
            f.write(random_text)
            output_size -= block_size

# Считываем размер из файла
with open('размер.txt', 'r') as size_file:
    output_size_mb = float(size_file.read())

# Переводим мегабайты в байты (1 MB = 1024 * 1024 байт)
output_size_bytes = int(output_size_mb * 1024 * 1024)

# Создаем файл с заданным размером
create_file('выход.txt', output_size_bytes)

print("Файл успешно создан.")