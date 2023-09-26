import psycopg2 
from base64 import b64encode,b64decode
from .serializers import GenreSerializer,MovieSerializer,UserSerializer,PaginateResponseMovie
from .database_constant_commands import *
from .decorators import command_decorator
from .database_utils import get_filtered_movie_by_genres_and_string,get_filtered_movie_by_string,get_favorite_filter

CONNECTION = psycopg2.connect(
        database="MovieApp",
        host="localhost",
        user="wertun",
        password="43554453",
        port="5432"
    )

MOVIE_PER_PAGE = 20

CURSOR = CONNECTION.cursor()

def b64crypt_encode(password):
    return b64encode(str(password).encode()).decode()

def b64crypt_decode(password):
    return b64decode(str(password).encode()).decode()



def destroy_database():
    try:
        CURSOR.execute(DESTROY_TABLES)
        CONNECTION.commit()
    except psycopg2.Error as error:
        print(error)

def create_database():
    try:
        CURSOR.execute(CREATE_TABLES)
        CONNECTION.commit()
    except psycopg2.Error as error:
        print(error)

@command_decorator
async def read_all_genres() -> list:
    CURSOR.execute(SELECT_ALL_GENRES)
    genres = CURSOR.fetchall()
    genres_list = []
    for genre in genres:
        genres_list.append(GenreSerializer(name=genre[0]))
    
    return genres_list

@command_decorator 
async def read_detail_movie(**kwargs) -> MovieSerializer:
    CURSOR.execute(f'''
    SELECT * FROM "movie" WHERE id = {kwargs['pk']}
    ''')
    movie = CURSOR.fetchone()
    CURSOR.execute(f'''
    SELECT * FROM "genre_movie" WHERE movie_id = {kwargs['pk']}
    ''')
    genres = CURSOR.fetchall()
    
    serialized = MovieSerializer.auto_fill(movie=movie,genres=genres)

    return serialized

@command_decorator
async def read_all_movie(**kwargs) -> PaginateResponseMovie:
    page = int(kwargs['page'])
    find_string = kwargs['string']
    fliter_genres = kwargs['genres']

    if fliter_genres != None and len(fliter_genres) > 0:
        movie = get_filtered_movie_by_genres_and_string(
            cursor=CURSOR,
            filter_genres=fliter_genres,
            find_string=find_string
        )
        max_pages = 1 if round(len(movie) / MOVIE_PER_PAGE) == 0 else round(len(movie) / MOVIE_PER_PAGE)
        movie = movie[0:MOVIE_PER_PAGE]
    else:
        movie = get_filtered_movie_by_string(
            cursor=CURSOR,
            find_string=find_string,
            per_page=MOVIE_PER_PAGE,
            page=page
        )
        max_pages = 1 if round(movie[0] / MOVIE_PER_PAGE) == 0 else round(movie[0] / MOVIE_PER_PAGE)
        movie = movie[1]

    serialized_list = []
    for m in movie:
        CURSOR.execute(f'''
        SELECT * FROM "genre_movie" WHERE movie_id = {int(m[0])};
        ''')
        genres = CURSOR.fetchall()
        serialized_list.append(MovieSerializer.auto_fill(movie=m,genres=genres))
        
    return PaginateResponseMovie(results=serialized_list,page=page,max_page=max_pages,search_string=find_string,filter_data={"genres":fliter_genres})

@command_decorator
async def read_all_favorite_movie(**kwargs) -> PaginateResponseMovie:
    page = int(kwargs['page'])
    find_string = kwargs['string']
    filter_genres = kwargs['genres']
    user = kwargs['user']

    movie = get_favorite_filter(
        cursor=CURSOR,
        find_string=find_string,
        user_id=user.id,
        per_page=MOVIE_PER_PAGE,
        page=page
    )

    max_pages = 1 if round(movie[0] / MOVIE_PER_PAGE) == 0 else round(movie[0] / MOVIE_PER_PAGE)

    serialized_list = []
    for m in movie[1]:
        CURSOR.execute(f'''
        SELECT * FROM "genre_movie" WHERE movie_id = {int(m[0])};
        ''')
        genres = CURSOR.fetchall()
        serialized_list.append(MovieSerializer.auto_fill(movie=m,genres=genres))
        
    return PaginateResponseMovie(results=serialized_list,page=page,max_page=max_pages,search_string=find_string,filter_data={"genres":filter_genres})

@command_decorator
async def read_detail_user_without_favorite(**kwargs) -> UserSerializer:
    CURSOR.execute(f'''
    SELECT * FROM "user" WHERE id = {kwargs['pk']};
    ''')
    user = CURSOR.fetchone()

    serialized_user = UserSerializer(id=user[0],username=user[1],email=user[2],password=user[3])

    return serialized_user

@command_decorator
async def create_user_db(**kwargs):
    user = kwargs['user']
    CURSOR.execute(f'''
    INSERT INTO "user" (username,email,password) VALUES ('{user.username}','{user.email}','{b64crypt_encode(password=user.password)}')
    ''')
    
    CONNECTION.commit()

@command_decorator
async def create_token(**kwargs):
    user_id = kwargs['user']
    token = kwargs['token']
    CURSOR.execute(f'''
    INSERT INTO "token" (token,user_id) VALUES ('{token}',{user_id});
    ''')
    CONNECTION.commit()

@command_decorator
async def delete_created_token(**kwargs):
    user_id = kwargs['user']
    CURSOR.execute(f'''
    DELETE FROM "token" WHERE user_id = {user_id};
    ''')
    CONNECTION.commit()

@command_decorator
async def get_auth_user(**kwargs):
    CURSOR.execute(f'''
    SELECT * FROM "user" WHERE username = '{kwargs['username']}'
    ''')

    user = CURSOR.fetchone()

    return user

@command_decorator
async def get_favorite(**kwargs) -> list:
    CURSOR.execute(f'''
    SELECT * FROM "user_movie" WHERE user_id = {int(kwargs['user'])}
    ''')
    favorites = CURSOR.fetchall()
    if len(favorites) == 0:
        return []
    serialized_fav = []
    command = f'''SELECT title FROM "movie" WHERE id IN ('''
    for item in favorites:
        command += str(item[1])+","
    command = command[0:len(command)-1] + ");"
    CURSOR.execute(command)
    movies = CURSOR.fetchall()
    for i in movies:
        serialized_fav.append(i[0])
    
    return serialized_fav

@command_decorator
async def movie_to_favorite(**kwargs):
    movie_id = kwargs['movie_id']
    user_id = kwargs['user']
    CURSOR.execute(f'''
    DO $$
    BEGIN
    IF EXISTS (SELECT FROM "user_movie" WHERE user_id = {user_id} AND movie_id = {movie_id}) THEN
    DELETE FROM "user_movie" WHERE user_id = {user_id} AND movie_id = {movie_id};
    ELSE
    INSERT INTO "user_movie" (user_id,movie_id) VALUES ({user_id},{movie_id});
    END IF;
    END $$
    ''')
    CONNECTION.commit()
    CURSOR.execute(f'''
    SELECT EXISTS (SELECT * FROM "user_movie" WHERE user_id={user_id} AND movie_id={movie_id})::int
    ''')
    if CURSOR.fetchall()[0][0] == 0:
        return True
    else:
        return False

