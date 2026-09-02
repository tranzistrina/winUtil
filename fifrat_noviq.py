def shift_text(text, initial_shift):
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    shifted_text = ''
    shift = initial_shift
    for char in text:
        if char.lower() in alphabet:
            is_upper = char.isupper()
            index = (alphabet.index(char.lower()) + shift) % len(alphabet)
            shifted_char = alphabet[index]
            if is_upper:
                shifted_char = shifted_char.upper()
            shifted_text += shifted_char
            # Увеличиваем сдвиг для следующей буквы в два раза
            shift *= 2
        else:
            shifted_text += char
    return shifted_text

def read_text_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_text_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

# Чтение текста из файлов
text_filename = 'текст.txt'
shift_filename = 'сдвиг.txt'
encrypted_filename = 'шифрат.txt'

text = read_text_from_file(text_filename)
shift = int(read_text_from_file(shift_filename))

# Применение шифрования
encrypted_text = shift_text(text, shift)

# Сохранение зашифрованного текста в файл
write_text_to_file(encrypted_text, encrypted_filename)

print("Текст успешно зашифрован и сохранен в файл", encrypted_filename)
