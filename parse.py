import psycopg2
import requests
from database.database import CONNECTION, CURSOR, command_decorator


@command_decorator
async def parse_data():
    url = "https://imdb-top-100-movies.p.rapidapi.com/"

    headers = {
        "X-RapidAPI-Key": "f68985d372mshcfdd5a2df4327ffp1e243fjsn91b13b6acaba",
        "X-RapidAPI-Host": "imdb-top-100-movies.p.rapidapi.com"
    }
    start_id = 1000
    response = requests.get(url, headers=headers)
    for movie in response.json():
        
        try:    
            res = requests.get(movie['thumbnail'], headers=headers)
            if res.status_code == 404:
                continue
        except requests.exceptions.RequestException:
            pass 
        
        try:
            CURSOR.execute(f'''
            INSERT INTO "movie" (id, title, description, raiting, reliased, image) VALUES ({start_id},
            '{str(movie['title']).replace("'","''")}',
            '{str(movie['description']).replace("'","''")}',
            {movie['rating']},{movie['year']},'{movie['thumbnail']}') ON CONFLICT DO NOTHING;
            ''')
        except psycopg2.Error:
            continue

        for genre in movie['genre']:
            CURSOR.execute(f'''
            INSERT INTO "genre" (name) VALUES ('{str(genre).replace("'","''")}') ON CONFLICT DO NOTHING;
            ''')
            CURSOR.execute(f'''
            INSERT INTO "genre_movie" (genre_id,movie_id) VALUES ('{str(genre).replace("'","''")}',
            {start_id}) ON CONFLICT DO NOTHING;
            ''')

            CONNECTION.commit()

        start_id += 1
