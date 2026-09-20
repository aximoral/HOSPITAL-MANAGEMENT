@echo off
echo Starting Hospital Management System...

echo Starting Backend API...
start cmd /k "python -m uvicorn backend.main:app --reload"

echo Starting Frontend UI...
start cmd /k "python -m streamlit run frontend/app.py"

echo Both servers are starting up! Your browser should open automatically.
