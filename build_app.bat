@echo off
echo Building Smart AI Assistant...
echo.

REM Check if in correct directory
if not exist "gui_app.py" (
    echo Error: gui_app.py not found. Please run this script from the project directory.
    pause
    exit /b 1
)

REM Install required packages if not already installed
echo Installing/checking required packages...
pip install -r requirements.txt

REM Build the application
echo.
echo Building executable with PyInstaller...
pyinstaller --clean --onefile --windowed --name="SmartAIAssistant" ^
    --add-data="plugins;plugins" ^
    --add-data="config.json;." ^
    --add-data="knowledge_base.json;." ^
    --add-data="README.md;." ^
    --add-data="LICENSE;." ^
    --hidden-import="tkinter" ^
    --hidden-import="tkinter.ttk" ^
    --hidden-import="tkinter.scrolledtext" ^
    --hidden-import="tkinter.messagebox" ^
    --hidden-import="speech_recognition" ^
    --hidden-import="pyttsx3" ^
    --hidden-import="requests" ^
    --hidden-import="bs4" ^
    --hidden-import="pyautogui" ^
    --hidden-import="psutil" ^
    --hidden-import="win32gui" ^
    --hidden-import="win32con" ^
    --hidden-import="win32api" ^
    gui_app.py

echo.
if exist "dist\SmartAIAssistant.exe" (
    echo ✅ Build successful! 
    echo.
    echo The executable is located at: dist\SmartAIAssistant.exe
    echo You can now distribute this file to other users.
    echo.
    echo Would you like to test the executable now? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo Starting the application...
        start "" "dist\SmartAIAssistant.exe"
    )
) else (
    echo ❌ Build failed. Check the output above for errors.
)

echo.
pause
