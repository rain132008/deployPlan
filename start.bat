@echo off
echo Starting AutoDeployDocs...

echo Building Frontend...
cd frontend
call npm run build
cd ..

echo Starting Backend...
cd backend
python app.py
