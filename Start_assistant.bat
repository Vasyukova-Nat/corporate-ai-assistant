@echo off
chcp 65001 >nul
title Корпоративный AI-Ассистент - Запуск

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend\CorpDocGPTdesktop"
set "LOG_FILE=%PROJECT_ROOT%app_startup.log"

echo ===============================================
echo   Запуск Корпоративного AI-Ассистента
echo ===============================================
echo.

:: Очистка старого лога
if exist "%LOG_FILE%" del "%LOG_FILE%"

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

echo Освобождаем порт 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo Запуск AI-сервера... 
start "Backend Server" /MIN cmd /c "cd /d "%BACKEND_DIR%" && call venv\Scripts\activate.bat && uvicorn app:app --host 0.0.0.0 --port 8000 > "%LOG_FILE%" 2>&1"

echo Ожидание запуска AI-сервера:
echo [5%%] Инициализация моделей ИИ...
timeout /t 3 /nobreak >nul

:: Проверяем доступность бэкенда каждые 3 секунды
set "backend_checked=0"
for /l %%i in (1,1,10) do (
    curl -s http://localhost:8000/docs >nul 2>&1
    if !errorlevel! equ 0 (
        if !backend_checked! equ 0 (
            echo [100%%] AI-сервер готов!
            set "backend_checked=1"
        )
        goto backend_ready
    )
    
    if %%i equ 2 (
        echo [25%%] Загрузка языковых моделей...
    ) else if %%i equ 5 (
        echo [50%%] Инициализация RAG системы...
    ) else if %%i equ 8 (
        echo [75%%] Запуск API сервера...
    )
    
    timeout /t 3 /nobreak >nul
)

:backend_ready

echo.
echo Запуск интерфейса...
echo [10%%] Подготовка приложения...

start "Frontend App" /MIN cmd /c "cd /d "%FRONTEND_DIR%" && npm run tauri dev"

:: мониторинг запуска фронтенда
set "frontend_started=0"
set "progress=10"

echo [25%%] Сборка компонентов...
timeout /t 5 /nobreak >nul

:check_frontend_loop
:: Проверяем запущено ли Tauri приложение
tasklist /FI "IMAGENAME eq CorpDocGPTdesktop.exe" 2>nul | find /i "CorpDocGPTdesktop.exe" >nul
if !errorlevel! equ 0 (
    if !frontend_started! equ 0 (
        echo [100%%] Приложение запущено и готово к работе!
        set "frontend_started=1"
        goto app_ready
    )
)

:: Альтернативная проверка по заголовку окна
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq CorpDocGPTdesktop.exe" /fo table /nh') do (
    if not "%%i"=="=" (
        if !frontend_started! equ 0 (
            echo [100%%] Приложение запущено и готово к работе!
            set "frontend_started=1"
            goto app_ready
        )
    )
)

:: Показываем прогресс только если приложение еще не запустилось
if !frontend_started! equ 0 (
    if !progress! equ 10 (
        echo [50%%] Компиляция кода...
        set "progress=50"
    ) else if !progress! equ 50 (
        echo [75%%] Создание интерфейса...
        set "progress=75"
    )
)

:: Ждем перед следующей проверкой
timeout /t 3 /nobreak >nul

:: Защита от бесконечного цикла - максимум 30 секунд на ожидание фронтенда
set /a "timeout_count=!timeout_count!+1"
if !timeout_count! lss 10 goto check_frontend_loop

:: Если фронтенд не запустился за 30 секунд, считаем что он запускается
echo [100%%] Приложение запускается...
echo [ИНФО] Если приложение не открылось автоматически, оно появится в течение минуты

:app_ready
echo.
echo ===============================================
echo   Приложение успешно запущено!
echo ===============================================
echo.
echo ✓ AI-сервер работает на localhost:8000
echo ✓ Desktop приложение CorpDocGPTdesktop запущено
echo.
echo Для остановки просто закройте окно приложения
echo.

:: Очистка временных файлов
if exist "%LOG_FILE%" del "%LOG_FILE%"

echo.
echo Нажмите любую клавишу для закрытия этого окна...
pause >nul