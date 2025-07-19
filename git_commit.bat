@echo off
echo ========================================
echo VGT Repository Git Helper
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    echo.
)

echo Current status:
git status --short
echo.

echo Adding all files...
git add .
echo.

echo Creating commit...
git commit -m "Complete VGT repository setup for March 2025 thesis"
echo.

echo Repository is ready!
echo.
echo Next steps:
echo 1. If not already done: git remote add origin https://github.com/Belowme77/Vibrational-Gravity-Theory.git
echo 2. Push to GitHub: git push -u origin main
echo    (or if branch exists: git push origin main)
echo.
echo If you need to switch branches:
echo   git checkout -b march-2025-thesis
echo   git push -u origin march-2025-thesis
echo.
pause
