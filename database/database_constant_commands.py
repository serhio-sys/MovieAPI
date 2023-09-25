
DESTROY_TABLES = '''
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public; 
    GRANT ALL ON SCHEMA public TO postgres;
    GRANT ALL ON SCHEMA public TO public;
'''

SELECT_ALL_GENRES = '''
    SELECT * FROM "genre"
'''

CREATE_TABLES = '''
    CREATE TABLE "genre"
    (
        name VARCHAR ( 50 ) UNIQUE NOT NULL PRIMARY KEY
    );
    CREATE TABLE "movie"
    (
        id serial PRIMARY KEY,
        title VARCHAR ( 50 ),
        description TEXT,
        image VARCHAR ( 255 ),
        reliased SMALLINT,
        raiting SMALLINT  
    );
    CREATE TABLE "genre_movie"
    (
        genre_id VARCHAR ( 50 ) NOT NULL,
        movie_id INT NOT NULL,
        PRIMARY KEY (genre_id, movie_id),
        FOREIGN KEY (genre_id)
            REFERENCES "genre" (name),
        FOREIGN KEY (movie_id)
            REFERENCES "movie" (id)           
    );
    CREATE TABLE "user"
    (
        id serial PRIMARY KEY,
        username VARCHAR ( 50 ) NOT NULL UNIQUE,
        email VARCHAR ( 100 ) NOT NULL,
        password VARCHAR ( 255 ) NOT NULL
    );
    CREATE TABLE "comment" 
    (
        id serial PRIMARY KEY,
        text TEXT,
        author_id INT NOT NULL,
        movie_id INT NOT NULL,
        FOREIGN KEY (author_id)
            REFERENCES "user" (id),
        FOREIGN KEY (movie_id)
            REFERENCES "movie" (id)
    );
    CREATE TABLE "user_movie"
    (
        user_id INT NOT NULL,
        movie_id INT NOT NULL,
        PRIMARY KEY (user_id,movie_id),
        FOREIGN KEY (user_id)
            REFERENCES "user" (id),
        FOREIGN KEY (movie_id)
            REFERENCES "movie" (id)
    );
'''

CREATE_TABLE_TOKEN = '''
    CREATE TABLE "token"
    (
        id serial PRIMARY KEY,
        token TEXT,
        user_id INT NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES "user" (id)
    );
'''