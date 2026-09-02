import math

# Функция для вычисления квадратных корней
def calculate_roots(a, b, c):
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None, None  # Нет действительных корней
    elif discriminant == 0:
        root = -b / (2*a)
        return root, None  # Один действительный корень
    else:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return root1, root2  # Два действительных корня

# Считывание данных из файлов
def read_coefficients(filename):
    with open(filename, 'r') as file:
        return float(file.readline().strip())

# Считывание коэффициентов из файлов
a = read_coefficients('a.txt')
b = read_coefficients('b.txt')
c = read_coefficients('c.txt')

# Вычисление квадратных корней
root1, root2 = calculate_roots(a, b, c)

# Запись результатов в файл
with open('математика.txt', 'w') as file:
    if root1 is None:
        file.write('Нет действительных корней\n')
    else:
        file.write(f'Первый корень: {root1}\n')
        if root2 is not None:
            file.write(f'Второй корень: {root2}\n')