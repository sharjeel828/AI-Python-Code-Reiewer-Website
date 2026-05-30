@echo off
title AI Code Reviewer Website
echo Starting AI Code Reviewer Website...
echo Opening http://127.0.0.1:5000 in your default browser...
start "" "http://127.0.0.1:5000"
venv\Scripts\python.exe app.py
pause
