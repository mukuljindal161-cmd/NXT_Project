@echo off
echo ========================================================
echo Starting College RAG Assistant Backend API (Port 8000)...
echo ========================================================
cd apps\api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
