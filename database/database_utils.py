def generate_command_with_genres_filter(filter_genres:list) -> str:
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

def generete_command_getting_movie_by_ids(find_string:str,movie_ids:tuple) -> str:
    command = f'''SELECT * FROM "movie" WHERE id IN ('''
    for i in list(movie_ids):
        command += f'{i[1]},'
    command = command[0:len(command)-2]
    if find_string != None:
        command += f"\n) AND LOWER(title) LIKE '%{find_string.lower()}%';"
    else:
        command += ");"
    return command

def get_filtered_movie_by_genres_and_string(cursor,filter_genres:list,find_string:str) -> tuple:
    command = generate_command_with_genres_filter(filter_genres)
    cursor.execute(command)
    movie_ids = cursor.fetchall()
    command = generete_command_getting_movie_by_ids(
        find_string=find_string,
        movie_ids=movie_ids
    )
    cursor.execute(command)
    return cursor.fetchall()

def get_filtered_movie_by_string(cursor,find_string:str,per_page:int,page:int) -> list:
    command = f'SELECT * FROM "movie" '
    returned_values = []
    bonus_string = ''
    if find_string != None:
        bonus_string += f'WHERE LOWER(title) LIKE \'%{find_string.lower()}%\' LIMIT {per_page*page} OFFSET {per_page*(page-1)};'
        count = cursor.execute('SELECT COUNT(*) FROM "movie" '+bonus_string)
        returned_values.append(cursor.fetchall()[0][0])
    else:
        bonus_string += f'LIMIT {per_page*page} OFFSET {per_page*(page-1)};'
    cursor.execute('SELECT COUNT(*) FROM "movie" ')
    returned_values.append(cursor.fetchall()[0][0])
    command += bonus_string
    cursor.execute(command)
    returned_values.append(cursor.fetchall())
    return returned_values