import mpmath

def compute_pi(precision):
    mpmath.mp.dps = precision  # Устанавливаем точность вычислений
    return str(mpmath.pi)  # Преобразуем результат в строку

def main():
    # Чтение числа из файла
    with open("число.txt", "r") as file:
        precision = int(file.read().strip())

    # Вычисление числа Пи
    result = compute_pi(precision)

    # Сохранение результата в файл
    with open("результат.txt", "w") as file:
        file.write(result)

if __name__ == "__main__":
    main()
