from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class GenreSerializer(BaseModel):
    name: str


class CommentSerializer(BaseModel):

    @staticmethod
    def auto_fill(comment, author):
        return CommentSerializer(
            id=comment[0],
            text=comment[1],
            author=author[0],
            movie_id=comment[3]
        )

    id: int
    text: str
    author: str
    movie_id: int


class BasePaginateResponse(BaseModel):
    results: list
    page: int
    max_page: int


class PaginateResponseMovie(BasePaginateResponse):
    search_string: Optional[str] = None
    filter_data: Optional[dict] = None


class UserSerializer(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None


class UserRegistrationSerializer(BaseModel):
    username: str = Field(..., min_length=4)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)


class UserLoginSerializer(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class MovieSerializer(BaseModel):

    @staticmethod
    def auto_fill(movie, genres):
        serialized = MovieSerializer()
        serialized.id = int(movie[0])
        serialized.title = movie[1]
        serialized.description = movie[2]
        serialized.image = movie[3]
        serialized.relised = int(movie[4])
        serialized.raiting = int(movie[5])

        for genre in genres:
            serialized.genres.append(GenreSerializer(name=genre[0]))

        return serialized

    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    relised: Optional[int] = None
    image: Optional[str] = None
    raiting: Optional[int] = None
    genres: Optional[list[GenreSerializer]] = list()
