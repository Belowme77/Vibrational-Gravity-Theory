@echo off
echo ========================================
echo Git Repository Setup for VGT
echo ========================================
echo.

echo Initializing git repository...
git init
echo.

echo Adding all files...
git add .
echo.

echo Creating initial commit...
git commit -m "Initial commit: Complete VGT repository for March 2025 thesis"
echo.

echo Setting up remote repository...
git remote add origin https://github.com/Belowme77/Vibrational-Gravity-Theory.git
echo.

echo Repository initialized!
echo.
echo Next steps:
echo 1. Make sure you're logged into GitHub
echo 2. Push to GitHub with: git push -u origin main
echo.
echo If the main branch doesn't exist on GitHub yet, you might need:
echo   git branch -M main
echo   git push -u origin main
echo.
echo If you want a separate branch for the March 2025 version:
echo   git checkout -b march-2025-thesis
echo   git push -u origin march-2025-thesis
echo.
pause
