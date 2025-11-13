@echo off
chcp 65001 >nul
title Установка AI-Ассистента

echo ===============================================
echo   Установка Корпоративного AI-Ассистента
echo ===============================================
echo.

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend\CorpDocGPTdesktop"

echo Проверка структуры проекта...
echo.

if not exist "%BACKEND_DIR%" (
    echo [ОШИБКА] Папка бэкенда не найдена!
    echo Создайте папку: backend
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo [ОШИБКА] Папка фронтенда не найдена!
    echo Создайте папку: frontend\CorpDocGPTdesktop
    pause
    exit /b 1
)

echo ✓ Структура проекта проверена
echo.

:install_python
echo [1/4] Проверка Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Установка Python...
    winget install Python.Python.3.11 -h --accept-package-agreements --accept-source-agreements
)
echo ✓ Python готов

:install_nodejs
echo.
echo [2/4] Проверка Node.js...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Установка Node.js...
    winget install OpenJS.NodeJS -h --accept-package-agreements --accept-source-agreements
)
echo ✓ Node.js готов

:setup_backend
echo.
echo [3/4] Настройка бэкенда...
cd /d "%BACKEND_DIR%"

echo Создание виртуального окружения...
python -m venv venv

echo Установка зависимостей Python...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if %errorLevel% neq 0 (
    echo Установка основных зависимостей...
    pip install fastapi uvicorn chromadb ollama
)
echo ✓ Бэкенд настроен

:setup_frontend
echo.
echo [4/4] Настройка фронтенда...
echo ЗАМЕЧАНИЕ: Установка фронтенда может занять 5-10 минут
echo.

:: Простой способ - запускаем отдельный cmd в нужной директории
start /wait cmd /c "cd /d "%FRONTEND_DIR%" && echo Установка npm зависимостей... && npm install && echo ✓ Фронтенд зависимости установлены"

echo.
echo ===============================================
echo   Установка завершена!
echo ===============================================
echo.
echo Что сделано:
echo ✓ Python и зависимости установлены
echo ✓ Node.js установлен  
echo ✓ Бэкенд настроен с виртуальным окружением
echo ✓ Фронтенд зависимости установлены
echo.
echo Теперь запустите Start_assistant_with_logging.bat
echo.
pause