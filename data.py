from datetime import datetime, timedelta

# Чтение количества дней из файла
try:
    with open('дни_до.txt', 'r') as days_file:
        days = int(days_file.read())
except FileNotFoundError:
    print("Файл 'дни_до.txt' не найден.")
    exit()
except ValueError:
    print("Неверный формат данных в файле 'дни_до.txt'.")
    exit()

# Получение текущей даты
current_date = datetime.now()

# Добавление количества дней
future_date = current_date + timedelta(days=days)

# Запись результата в файл
try:
    with open('дата.txt', 'w') as output_file:
        output_file.write(future_date.strftime('%Y-%m-%d'))
    print("Дата успешно записана в файл 'дата.txt'.")
except Exception as e:
    print(f"Ошибка при записи в файл: {e}")