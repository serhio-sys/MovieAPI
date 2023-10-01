from pydantic import BaseModel, EmailStr
from database.database import CONNECTION,CURSOR
from typing import Optional

tables = {
    "movie":"(title,description,reliased,image,raiting)",
    "genre":"(name)"
}

class BasedSerializer(BaseModel):
    
    @staticmethod
    def auto_create_list(serializer_class,objects) -> list:
        serialized_list = []

        if hasattr(serializer_class,'auto_fill'):
            for i in objects:
                serialized_list.append(serializer_class.auto_fill(i))

        return serialized_list
    
    @staticmethod
    def save_to_db(serializer_data,table_name):
        fields = []
        values = []
        for attr, value in vars(serializer_data).items():
            if attr != "id":
                fields.append(attr)
                values.append(value)
        if len(values) > 1:
            values = str(tuple(values))
            values = values[0:len(values)-1] + ");"
        else:
            values = str(tuple(values))
            values = values[0:len(values)-2] + ");"
        fields = str(tuple(fields))
        fields = fields[0:len(fields)-2] + ")"
        fields = fields.replace('\'','')
        CURSOR.execute(f"INSERT INTO \"{table_name}\" {fields} VALUES {values}")
        CONNECTION.commit()

class CommentAdminSerializer(BasedSerializer):
    @staticmethod
    def auto_fill(comment):
        serialized = CommentAdminSerializer()
        serialized.id = comment[0]
        serialized.text = comment[1]
        serialized.author_id = comment[2]
        serialized.movie_id = comment[3]

        return serialized

    id : Optional[int] = None
    text : Optional[str] = None
    author_id : Optional[int] = None
    movie_id : Optional[int] = None

class MovieAdminSerializer(BasedSerializer):

    @staticmethod
    def auto_fill(movie):
        serialized = MovieAdminSerializer()
        serialized.id = int(movie[0])
        serialized.title = movie[1]
        serialized.description = movie[2]
        serialized.image = movie[3]
        serialized.relised = int(movie[4])
        serialized.raiting = int(movie[5])
        
        return serialized

    id : Optional[int] = None
    title : Optional[str] = None
    description : Optional[str] = None
    relised : Optional[int] = None
    image : Optional[str] = None
    raiting : Optional[int] = None

class GenreAdminSerializer(BasedSerializer):

    @staticmethod
    def auto_fill(genre):
        serialized = GenreAdminSerializer()
        serialized.name = genre[0]
        
        return serialized

    name : Optional[str] = None

class UserAdminSerializer(BasedSerializer):

    @staticmethod
    def auto_fill(user):
        serialized = UserAdminSerializer()
        serialized.id = user[0]
        serialized.username = user[1]
        serialized.email = user[2]
        serialized.password = user[3] 

        return serialized

    id : Optional[int] = None
    username : Optional[str] = None
    email : Optional[str] = None
    password : Optional[str] = None
