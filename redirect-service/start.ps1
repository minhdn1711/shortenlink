# Chạy redirect trên port 9004 (tunnel phanmemcongnghevip.online → localhost:9004)
$env:BACKEND_URL = if ($env:BACKEND_URL) { $env:BACKEND_URL } else { "http://127.0.0.1:8000" }
$env:PORT = if ($env:PORT) { $env:PORT } else { "9004" }

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

.\.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port $env:PORT
