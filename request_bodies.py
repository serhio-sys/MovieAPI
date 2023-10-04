from pydantic import BaseModel
from typing import Optional


class CommentRequest(BaseModel):
    movie_id: Optional[int] = None
    author_id: Optional[int] = None
    text: Optional[str] = ""


class MovieRequest(BaseModel):
    page: Optional[int] = 1
    string: Optional[str] = None
    genres: Optional[list] = None
