@echo off
cd /d C:\Users\HP\Documents\MADDY\calender
start "" python calender.py
timeout /t 2 >nul
start "" http://127.0.0.1:5000
