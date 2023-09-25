from pydantic import BaseModel
from typing import Optional

class MovieRequest(BaseModel):
    page : Optional[int] = 1
    string : Optional[str] = None
    genres : Optional[list] = None