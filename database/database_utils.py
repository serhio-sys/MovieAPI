import psycopg2
from database.serializers import MovieSerializer


DATABASE_CONNECTION_SETTINGS = {
    "database": "MovieApp",
    "host": "localhost",
    "user": "wertun",
    "password": "43554453",
    "port": "5432"
}


def create_connection():
    while True:
        try:
            connection = psycopg2.connect(**DATABASE_CONNECTION_SETTINGS)
            cursor = connection.cursor()
            return connection, cursor
        except psycopg2.Error as error:
            if isinstance(error, errors.InFailedSqlTransaction):
                # Roll back the transaction and retry
                cursor.connection.rollback()
                continue
            else:
                # Handle other exceptions here if needed
                raise


def get_full_movies_info(cursor, movies: list | tuple) -> list:
    serialized_list = []
    for m in movies:
        cursor.execute(f'''
        SELECT * FROM "genre_movie" WHERE movie_id = {int(m[0])};
        ''')
        genres = cursor.fetchall()
        serialized_list.append(MovieSerializer.auto_fill(movie=m, genres=genres))
    return serialized_list


def generate_command_with_genres_filter(filter_genres: list) -> str:
    command = f'''SELECT * FROM "genre_movie" WHERE '''
    string = "("
    for i in range(len(filter_genres)):
        string += f'genre_id = \'{filter_genres[i]}\''
        if i == len(filter_genres) - 1:
            string += ')'
        else:
            string += ' OR '
    for i in range(len(filter_genres)):
        command += f'\n{string}'
        if i == len(filter_genres) - 1:
            command += ';'
        else:
            command += '\n AND '
    return command


def generate_command_favorite_movie(user_id: int) -> str:
    command = f'''
    SELECT * FROM "user_movie" WHERE user_id = {user_id};
    '''
    return command


def get_favorite_filter(cursor, find_string: str, user_id: int, per_page: int, page: int) -> list:
    cursor.execute(generate_command_favorite_movie(user_id))
    returned_values = []
    movie_ids = cursor.fetchall()
    if len(movie_ids) == 0:
        return [1, []]
    command = f'SELECT * FROM "movie" WHERE id IN ('
    bonus_string = ''
    for movie_id in movie_ids:
        command += f'{movie_id[1]},'
    if find_string is not None:
        bonus_string += f'AND LOWER(title) LIKE \'%{find_string.lower()}%\''
    command = command[
              0:len(command) - 1] + ") " + bonus_string + f" LIMIT {per_page * page} OFFSET {per_page * (page - 1)};"
    cursor.execute(command)
    movie = cursor.fetchall()
    command_count = command.replace('*', "COUNT(*)")
    cursor.execute(command_count)
    returned_values.append(cursor.fetchall()[0][0])
    returned_values.append(movie)
    return returned_values


def generate_command_getting_movie_by_ids(find_string: str, movie_ids: tuple) -> str:
    command = f'''SELECT * FROM "movie" WHERE id IN ('''
    for i in list(movie_ids):
        command += f'{i[1]},'
    command = command[0:len(command) - 2]
    if find_string is not None:
        command += f"\n) AND LOWER(title) LIKE '%{find_string.lower()}%';"
    else:
        command += ");"
    return command


def get_filtered_movie_by_genres_and_string(cursor, filter_genres: list, find_string: str) -> tuple:
    command = generate_command_with_genres_filter(filter_genres)
    cursor.execute(command)
    movie_ids = cursor.fetchall()
    command = generate_command_getting_movie_by_ids(
        find_string=find_string,
        movie_ids=movie_ids
    )
    cursor.execute(command)
    return cursor.fetchall()


def get_filtered_movie_by_string(cursor, find_string: str, per_page: int, page: int) -> list:
    command = f'SELECT * FROM "movie" '
    returned_values = []
    bonus_string = ''
    if find_string is not None:
        bonus_string += f'WHERE LOWER(title) LIKE \'%{find_string.lower()}%\' LIMIT {per_page * page} OFFSET {per_page * (page - 1)};'
        cursor.execute('SELECT COUNT(*) FROM "movie" ' + bonus_string)
    else:
        bonus_string += f'LIMIT {per_page * page} OFFSET {per_page * (page - 1)};'
    cursor.execute('SELECT COUNT(*) FROM "movie" ')
    returned_values.append(cursor.fetchall()[0][0])
    command += bonus_string
    cursor.execute(command)
    returned_values.append(cursor.fetchall())
    return returned_values
