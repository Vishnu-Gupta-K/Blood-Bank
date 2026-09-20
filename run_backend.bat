@echo off
echo Starting Blood Bank Backend Server...
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
pause