@echo off
chcp 65001 >nul
echo 启动OCR截图工具...
echo 快捷键: Ctrl+Alt+S (可在设置中修改)
echo 右键点击也可以触发
echo.
echo 程序将在系统托盘运行，右键点击托盘图标打开菜单
echo 按 Ctrl+C 退出（如果看到控制台窗口）
echo.
cd /d "%~dp0"
python main.py
pause
