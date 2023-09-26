from fastapi import APIRouter, Body
from fastapi.exceptions import HTTPException
from database.database import read_detail_movie,read_all_favorite_movie,movie_to_favorite, read_all_genres, read_all_movie, create_user_db, get_auth_user, b64crypt_decode, get_favorite
from database.serializers import UserRegistrationSerializer, UserLoginSerializer
from request_body import MovieRequest
from parse import parse_data
from dependencies import User
from auth.auth import generate_token,LoginResponse

router = APIRouter()

@router.post("/favorite-movie/")
async def favorite_movie(user : User, movie_data : MovieRequest):
    page = movie_data.page
    string = movie_data.string 
    genres = movie_data.genres
    movies = await read_all_favorite_movie(
        user=user,
        page=page,
        string=string,
        genres=genres
    )
    return movies

@router.post("/to-favorite/{pk}/")
async def add_to_favorite(user : User, pk):
    return await movie_to_favorite(user=user.id,movie_id=pk)

@router.get("/favorite/")
async def favorite(user : User):
    return await get_favorite(user=user.id)


@router.post("/auth/users/")
async def create_user(user:UserRegistrationSerializer):
    await create_user_db(user=user)
    return "Success"

@router.get("/jwt/user")
async def test2(user : User):
    print(user)
    return ""

@router.post("/jwt/token/")
async def login(user:UserLoginSerializer):
    user_db = await get_auth_user(username=user.username)
    if user.password == b64crypt_decode(user_db[3]):
        token = await generate_token(user_db)
        return LoginResponse(id=int(user_db[0]),token=token,username=user_db[1],email=user_db[2])
    else:
        raise HTTPException(status_code=401,
                            detail="Invalid credentials!")

@router.post("/parse/")
async def parse(data = Body()):
    await parse_data()
    return "Success"

@router.get("/genre/")
async def home():
    genres = await read_all_genres()
    return genres

@router.get("/movie/{pk}/")
async def detail_movie(pk):
    movie = await read_detail_movie(pk=pk)
    return movie

@router.get("/movie/")
async def movie(data = Body()):
    movie = await read_all_movie(page=1)
    return movie

@router.post("/movie/")
async def movie(movie_data:MovieRequest):
    page = movie_data.page
    string = movie_data.string 
    genres = movie_data.genres
    movie = await read_all_movie(page=page,string=string,genres=genres)
    return movie