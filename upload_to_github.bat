@echo off
echo Connecting to GitHub repository...
echo.

REM Add the GitHub repository as remote origin
git remote add origin https://github.com/Dolonia333/Smart-Local-AI-Assistant.git

REM Verify the remote was added
echo Remote repository added:
git remote -v
echo.

REM Push your code to GitHub
echo Pushing code to GitHub...
git push -u origin master

echo.
echo ✅ Upload complete! Your project is now on GitHub at:
echo https://github.com/Dolonia333/Smart-Local-AI-Assistant
pause
