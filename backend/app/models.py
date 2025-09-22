# app/models.py
from pydantic import BaseModel

class Ask(BaseModel):
    question: str
