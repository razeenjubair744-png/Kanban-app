import sqlite3
from collections.abc import Generator
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .ai import call_openrouter
from .db import (
    get_board_for_username,
    get_connection,
    get_user_by_token,
    get_user_by_username,
    initialize_database,
    save_board_for_username,
)
from .schemas import AIRequest, AIResponse, BoardData, LoginRequest, LoginResponse

load_dotenv()
initialize_database()

app = FastAPI(title="Kanban Studio API")

build_dir = Path(__file__).resolve().parents[1] / "frontend" / "out"


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def get_current_username(
    authorization: Optional[str] = Header(None), db: sqlite3.Connection = Depends(get_db)
) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token.")

    token = authorization.split(" ", 1)[1].strip()
    user = get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user["username"]


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: sqlite3.Connection = Depends(get_db)) -> LoginResponse:
    user = get_user_by_username(db, request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return LoginResponse(username=user["username"], token=user["token"])


@app.get("/api/board", response_model=BoardData)
def get_board(
    username: str = Depends(get_current_username),
    db: sqlite3.Connection = Depends(get_db),
) -> BoardData:
    board = get_board_for_username(db, username)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found.")
    return board


@app.patch("/api/board", response_model=BoardData)
def update_board(
    board: BoardData,
    username: str = Depends(get_current_username),
    db: sqlite3.Connection = Depends(get_db),
) -> BoardData:
    save_board_for_username(db, username, board)
    return board


@app.post("/api/ai", response_model=AIResponse)
def ai_route(
    request: AIRequest,
    username: str = Depends(get_current_username),
    db: sqlite3.Connection = Depends(get_db),
) -> AIResponse:
    response = call_openrouter(request)
    if response.boardUpdates is not None:
        save_board_for_username(db, username, response.boardUpdates)
    return response


if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="frontend")
else:
    @app.get("/{path:path}")
    def root(path: str = "") -> HTMLResponse:
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
