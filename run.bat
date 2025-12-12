@echo off
chcp 65001 >nul
echo ========================================
echo   台股歷史資料快速下載工具
echo ========================================
echo.
echo 正在啟動應用程式...
echo.

cd /d "%~dp0"
streamlit run stock_downloader.py

pause
