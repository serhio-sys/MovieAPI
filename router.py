from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from database.database import read_detail_movie, delete_comment, get_comments, create_comment, read_all_favorite_movie,\
    movie_to_favorite, read_all_genres, read_all_movie, create_user_db, get_auth_user, b64crypt_decode, get_favorite
from database.serializers import UserRegistrationSerializer, UserLoginSerializer
from request_bodies import MovieRequest, CommentRequest
from parse import parse_data
from dependencies import User
from auth.auth import generate_token, LoginResponse
from admin.views import admin_router, AdminView

router = APIRouter()

AdminView("movie")
AdminView("genre")
AdminView("token")
AdminView("user")
AdminView("comment")

router.include_router(prefix="/admin", router=admin_router)


@router.post("/favorite-movie/")
async def favorite_movie(user: User, movie_data: MovieRequest):
    page = movie_data.page
    string = movie_data.string 
    genres = movie_data.genres
    movies = read_all_favorite_movie(
        user=user,
        page=page,
        string=string,
        genres=genres
    )
    return movies


@router.delete('/comment/{pk}/')
async def delete_comment_route(pk: int, user: User):
    delete_comment(comment_id=pk, author_id=user.id)
    return JSONResponse({}, status_code=status.HTTP_204_NO_CONTENT)


@router.post('/create-comment/{pk}/')
async def create_comment_route(pk: int, user: User, comment_data: CommentRequest):
    comment_data.author_id = user.id
    comment_data.movie_id = pk
    create_comment(data=comment_data)
    return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.post("/to-favorite/{pk}/")
async def add_to_favorite(user: User, pk):
    return movie_to_favorite(user=user.id, movie_id=pk)


@router.get("/favorite/")
async def favorite(user: User):
    return get_favorite(user=user.id)


@router.get("/comments/{pk}/")
async def comments(pk: int, page: int = 1):
    return get_comments(movie_id=pk, page=page)


@router.post("/auth/users/")
async def create_user(user: UserRegistrationSerializer):
    error = create_user_db(user=user)
    if error:
        return JSONResponse(error, status_code=status.HTTP_400_BAD_REQUEST)
    return "Success"


@router.post("/jwt/token/")
async def login(user: UserLoginSerializer):
    user_db = get_auth_user(username=user.username)
    if user.password == b64crypt_decode(user_db[3]):
        token = generate_token(user_db)
        return LoginResponse(id=int(user_db[0]), token=token, username=user_db[1], email=user_db[2])
    else:
        raise HTTPException(status_code=401,
                            detail="Invalid credentials!")


@router.post("/parse/")
async def parse():
    await parse_data()
    return "Success"


@router.get("/genre/")
async def home():
    genres = read_all_genres()
    return genres


@router.get("/movie/{pk}/")
async def detail_movie(pk):
    detail_movie_response = read_detail_movie(pk=pk)
    return detail_movie_response


@router.get("/movie/")
async def movie():
    movie_response = read_all_movie(page=1)
    return movie_response


@router.post("/movie/")
async def movie(movie_data: MovieRequest):
    page = movie_data.page
    string = movie_data.string 
    genres = movie_data.genres
    movie_response = read_all_movie(page=page, string=string, genres=genres)
    return movie_response
