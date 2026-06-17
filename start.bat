@echo off
chcp 65001 > nul
title Запуск программы расчета дебита
echo =======================================================
echo Запуск приложения "Расчет дебита горизонтальной скважины"
echo =======================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    echo [OK] Виртуальное окружение найдено. Активируем...
    call .venv\Scripts\activate.bat
) else (
    echo [ВНИМАНИЕ] Виртуальное окружение 'venv' не найдено.
    echo Скрипт попытается использовать глобальный Python.
)

echo.
echo [ИНФО] Установка зависимостей (Flask)...
pip install flask

echo [OK] Запуск веб-сервера...
start http://127.0.0.1:5000
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Приложение завершило работу с ошибкой. Пожалуйста, проверьте текст выше.
    pause
)

if exist ".venv\Scripts\activate.bat" (
    call deactivate
)