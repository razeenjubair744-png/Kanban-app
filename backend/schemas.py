from typing import Dict, List, Optional

from pydantic import BaseModel


class Card(BaseModel):
    id: str
    title: str
    details: str


class Column(BaseModel):
    id: str
    title: str
    cardIds: List[str]


class BoardData(BaseModel):
    columns: List[Column]
    cards: Dict[str, Card]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    token: str


class AIRequest(BaseModel):
    prompt: str
    board: BoardData
    history: Optional[List[Dict[str, str]]] = None


class AIResponse(BaseModel):
    message: str
    boardUpdates: Optional[BoardData] = None
