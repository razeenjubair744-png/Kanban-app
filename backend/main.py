import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Kanban Studio API")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from Kanban Studio backend"}

build_dir = Path(__file__).resolve().parents[1] / "frontend" / "out"

if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="frontend")
else:
    @app.get("/")
    def root() -> HTMLResponse:
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Kanban Studio API</title>
          </head>
          <body style="font-family:system-ui, sans-serif; margin:0; padding:40px; background:#f7f8fb; color:#032147;">
            <div style="max-width:720px; margin:auto; padding:32px; background:#fff; border-radius:24px; box-shadow:0 24px 80px rgba(3,33,71,0.08);">
              <h1>Kanban Studio backend</h1>
              <p>This FastAPI backend is running and ready to serve the app.</p>
              <p>Visit <code>/api/health</code> for a health check.</p>
            </div>
          </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
