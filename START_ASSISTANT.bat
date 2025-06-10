@echo off
title Smart AI Assistant
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🤖 Smart Local Assistant                  ║
echo ║                     Quick Start Menu                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Select mode:
echo   1. Learning Mode (Self-Learning AI) - NEW RECOMMENDED
echo   2. Enhanced Mode (Voice + Text)
echo   3. Text-Only Mode
echo   4. Voice-Only Mode  
echo   5. Original Basic Mode
echo   6. Setup / Check Dependencies
echo   7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo Starting Learning Mode (Self-Learning AI)...
    python start_assistant.py learning
) else if "%choice%"=="2" (
    echo Starting Enhanced Mode...
    python start_assistant.py pro
) else if "%choice%"=="3" (
    echo Starting Text-Only Mode...
    python start_assistant.py text
) else if "%choice%"=="4" (
    echo Starting Voice-Only Mode...
    python start_assistant.py voice
) else if "%choice%"=="5" (
    echo Starting Basic Mode...
    python start_assistant.py basic
) else if "%choice%"=="5" (
    } else if "%choice%"=="6" (
    echo Running Setup...
    python start_assistant.py setup
    pause
) else if "%choice%"=="7" (
    echo Goodbye!
    exit /b
) else (
    echo Invalid choice. Please run the script again.
    pause
)

pause
