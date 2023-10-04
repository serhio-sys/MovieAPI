from typing import Annotated

from fastapi import Depends, Request
from database.serializers import UserSerializer
from auth.auth import decrypt_user


async def user(request: Request) -> UserSerializer | None:
    try:
        token = request.headers.get("authorization").split(" ")[1]
        return decrypt_user(token)
    except IndexError or Exception:
        return None

User = Annotated[UserSerializer, Depends(user)]
