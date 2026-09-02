@echo off
rem Переходим в каталог со скриптом
cd "путь_к_вашему_скрипту"

rem Устанавливаем необходимые переменные окружения
set PYTHONPATH=%PYTHONPATH%;%CD%
set PATH=%PATH%;%CD%

rem Путь к иконке
set ICON_PATH="C:\Users\lakh\Desktop\hy\icon.ico"

rem Компилируем скрипт в .exe файл с иконкой
pyinstaller -w --onefile --icon %ICON_PATH% filoobmenik.py

rem Пауза для того, чтобы увидеть вывод в случае ошибок
pause