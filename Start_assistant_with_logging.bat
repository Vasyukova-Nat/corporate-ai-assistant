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
    echo Запустите сначала Install.bat
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo [ОШИБКА] Папка фронтенда не найдена!
    echo Запустите сначала Install.bat
    pause
    exit /b 1
)

echo Проверка настроек бэкенда...
if not exist "%BACKEND_DIR%\venv\" (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo Запустите Install.bat для настройки
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [ОШИБКА] Файл activate.bat не найден в venv!
    echo Переустановите виртуальное окружение
    pause
    exit /b 1
)

echo Проверка настроек фронтенда...
if not exist "%FRONTEND_DIR%\node_modules\" (
    echo [ОШИБКА] Node.js зависимости не установлены!
    echo Запустите Install.bat для настройки
    pause
    exit /b 1
)

echo Освобождаем порт 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo [ПРЕДУПРЕЖДЕНИЕ] Порт 8000 занят процессом PID %%a
    echo Закрываем процесс...
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo.
echo [1/2] Запуск AI-сервера (бэкенд)...
cd /d "%BACKEND_DIR%"

:: Проверяем существование activate.bat перед вызовом
if not exist "venv\Scripts\activate.bat" (
    echo [КРИТИЧЕСКАЯ ОШИБКА] venv\Scripts\activate.bat не существует!
    echo Текущий путь: %CD%
    echo Содержимое папки venv\Scripts\:
    if exist "venv\Scripts\" dir "venv\Scripts\"
    pause
    exit /b 1
)

:: Альтернативный способ активации venv
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось активировать виртуальное окружение!
    echo Пробуем альтернативный метод...
    
    :: Пробуем напрямую вызвать Python из venv
    if exist "venv\Scripts\python.exe" (
        echo Запуск через прямое обращение к Python...
        start "Backend Server" cmd /k "cd /d "%BACKEND_DIR%" && "venv\Scripts\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8000"
    ) else (
        echo [ОШИБКА] python.exe не найден в venv!
        pause
        exit /b 1
    )
) else (
    echo Виртуальное окружение активировано успешно!
    echo Запуск FastAPI сервера...
    start "Backend Server" cmd /k "cd /d "%BACKEND_DIR%" && call venv\Scripts\activate.bat && echo [БЭКЕНД] Сервер запускается... && uvicorn app:app --host 0.0.0.0 --port 8000 && pause"
)

:: Ожидание запуска бэкенда с прогрессом
echo.
echo Ожидание запуска AI-сервера...
for /l %%i in (1,1,20) do (
    set /a "percent=%%i*5"
    echo [!percent!%%] Загрузка сервера...
    
    curl -s http://localhost:8000/docs >nul 2>&1
    if !errorlevel! equ 0 (
        echo [100%%] AI-сервер готов!
        goto backend_ready
    )
    timeout /t 2 /nobreak >nul
)

:backend_ready

echo.
echo [2/2] Запуск интерфейса (фронтенд)...
cd /d "%FRONTEND_DIR%"

if exist "node_modules\.bin\tauri.cmd" (
    echo Запуск Tauri приложения...
    start "Frontend App" cmd /k "cd /d "%FRONTEND_DIR%" && echo [ФРОНТЕНД] Приложение запускается... && npm run tauri dev && pause"
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] Tauri CLI не найден, пробуем напрямую...
    start "Frontend App" cmd /k "cd /d "%FRONTEND_DIR%" && echo [ФРОНТЕНД] Приложение запускается... && npx tauri dev && pause"
)

echo.
echo ===============================================
echo   Приложение запускается!
echo ===============================================
echo.
echo ✓ AI-сервер: http://localhost:8000
echo ✓ Документация API: http://localhost:8000/docs
echo ✓ Desktop приложение открывается...
echo.
echo Для остановки закройте оба окна (Backend Server и Frontend App)
echo.

echo Нажмите любую клавишу чтобы закрыть это окно...
pause >nul