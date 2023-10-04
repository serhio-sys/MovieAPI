import psycopg2.errors
from pydantic import BaseModel
from database.database import CONNECTION, CURSOR, b64crypt_encode
from typing import Optional


class BasedSerializer(BaseModel):
    @staticmethod
    def get_object(serializer_class, table_name: str, pk: int | str):
        if hasattr(serializer_class, 'auto_fill'):
            while True:
                try:
                    if table_name == "genre":
                        CURSOR.execute(f"SELECT * FROM \"{table_name}\" WHERE name = '{pk}';")
                    else:
                        CURSOR.execute(f"SELECT * FROM \"{table_name}\" WHERE id = {pk};")
                    i = CURSOR.fetchone()
                    return i
                except psycopg2.errors.InFailedSqlTransaction:
                    CONNECTION.rollback()

    @staticmethod
    def update_model(serializer_data, table_name: str, pk: int | str) -> None:
        command = f'''UPDATE {table_name} SET '''
        for attr, value in vars(serializer_data).items():
            if attr == "id":
                continue
            try:
                int(value)
                command += f"{attr} = {value},"
            except ValueError:
                command += f"{attr} = '{value}',"
        command = command[0:len(command) - 1]
        if table_name == "genre":
            command += f" WHERE name = '{pk}';"
        else:
            command += f" WHERE id = {pk};"
        CURSOR.execute(command)
        CONNECTION.commit()

    @staticmethod
    def auto_create_list(serializer_class, objects) -> list:
        serialized_list = []

        if hasattr(serializer_class, 'auto_fill'):
            for i in objects:
                serialized_list.append(serializer_class.auto_fill(i))

        return serialized_list

    @staticmethod
    def delete_from_db(primary, table_name: str) -> None:
        if table_name == "genre":
            CURSOR.execute(f"DELETE FROM \"{table_name}\" WHERE name = '{primary}';")
        else:
            CURSOR.execute(f"DELETE FROM \"{table_name}\" WHERE id = {primary};")
        CONNECTION.commit()

    @staticmethod
    def save_to_db(serializer_data, table_name: str) -> None:
        fields = []
        values = []
        for attr, value in vars(serializer_data).items():
            if attr == "password":
                fields.append(attr)
                values.append(b64crypt_encode(value))
                continue
            if attr != "id":
                fields.append(attr)
                values.append(value)
        if len(values) > 1:
            values = str(tuple(values))
            values = values[0:len(values) - 1] + ");"
        else:
            values = str(tuple(values))
            values = values[0:len(values) - 2] + ");"
        fields = str(tuple(fields))
        fields = fields[0:len(fields) - 2] + ")"
        fields = fields.replace('\'', '')
        CURSOR.execute(f"INSERT INTO \"{table_name}\" {fields} VALUES {values}")
        CONNECTION.commit()


class TokenAdminSerializer(BasedSerializer):
    @staticmethod
    def auto_fill(token):
        serialized = TokenAdminSerializer()
        serialized.id = token[0]
        serialized.token = token[1]
        serialized.user_id = token[2]

        return serialized

    id: Optional[int] = None
    token: Optional[str] = None
    user_id: Optional[int] = None


class CommentAdminSerializer(BasedSerializer):
    @staticmethod
    def auto_fill(comment):
        serialized = CommentAdminSerializer()
        serialized.id = comment[0]
        serialized.text = comment[1]
        serialized.author_id = comment[2]
        serialized.movie_id = comment[3]

        return serialized

    id: Optional[int] = None
    text: Optional[str] = None
    author_id: Optional[int] = None
    movie_id: Optional[int] = None


class MovieAdminSerializer(BasedSerializer):

    @staticmethod
    def auto_fill(movie):
        serialized = MovieAdminSerializer()
        serialized.id = int(movie[0])
        serialized.title = movie[1]
        serialized.description = movie[2]
        serialized.reliased = int(movie[4])
        serialized.image = movie[3]
        serialized.raiting = int(movie[5])

        return serialized

    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    reliased: Optional[int] = None
    raiting: Optional[int] = None


class GenreAdminSerializer(BasedSerializer):

    @staticmethod
    def auto_fill(genre):
        serialized = GenreAdminSerializer()
        serialized.name = genre[0]

        return serialized

    name: Optional[str] = None


class UserAdminSerializer(BasedSerializer):

    @staticmethod
    def auto_fill(user):
        serialized = UserAdminSerializer()
        serialized.id = user[0]
        serialized.username = user[1]
        serialized.email = user[2]
        serialized.password = user[3]

        return serialized

    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
