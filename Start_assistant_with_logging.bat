@echo off
chcp 65001 >nul
title Корпоративный AI-Ассистент - Запуск

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend\CorpDocGPTdesktop"

echo ===============================================
echo   Запуск Корпоративного AI-Ассистента
echo ===============================================
echo.

:: Проверка существования директорий
if not exist "%BACKEND_DIR%" (
    echo [ОШИБКА] Папка бэкенда не найдена!
    echo Запустите сначала install_and_setup.bat
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo [ОШИБКА] Папка фронтенда не найдена!
    echo Запустите сначала install_and_setup.bat
    pause
    exit /b 1
)

:: Функция для проверки порта
:check_port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo [ПРЕДУПРЕЖДЕНИЕ] Порт 8000 занят процессом PID %%a
    echo Закрываем процесс...
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo Запуск бэкенда (FastAPI сервер)...
start "Backend Server" cmd /k "cd /d "%BACKEND_DIR%" && call venv\Scripts\activate.bat && echo [БЭКЕНД] Сервер запускается... && uvicorn app:app --host 0.0.0.0 --port 8000 && pause"

echo Ожидание запуска бэкенда (40 секунд)...
timeout /t 40 /nobreak >nul

:: Проверяем доступность бэкенда
curl -s http://localhost:8000/docs >nul 2>&1
if %errorLevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Бэкенд не ответил, продолжаем запуск...
)

echo Запуск фронтенда (Tauri приложение)...
start "Frontend App" cmd /k "cd /d "%FRONTEND_DIR%" && echo [ФРОНТЕНД] Приложение запускается... && npm run tauri dev && pause"

echo.
echo ===============================================
echo   Приложение запускается!
echo ===============================================
echo.
echo Откроется два окна:
echo 1. Backend Server - API сервер на порту 8000
echo 2. Frontend App - Desktop приложение
echo Для остановки просто закройте оба окна.
echo.

pause