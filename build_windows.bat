@echo off
chcp 65001 >nul
echo ============================================
echo   维修工单系统 - Windows 桌面版打包
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/3] 打包中...
pyinstaller --noconfirm --onefile --windowed ^
    --name "维修工单系统" ^
    --add-data "config.py;." ^
    --add-data "api_client.py;." ^
    --hidden-import "kivy_deps.glew" ^
    --hidden-import "kivy_deps.sdl2" ^
    --hidden-import "kivy_deps.angle" ^
    main.py

echo [3/3] 完成!
echo.
echo 可执行文件位于: dist\维修工单系统.exe
echo.
pause
