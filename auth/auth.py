from pydantic import BaseModel
from datetime import datetime
from database.database import create_token,delete_created_token,b64crypt_decode,b64crypt_encode
from database.serializers import UserSerializer

def generate_token(user) -> str:
    user_string = str(datetime.utcnow())+"|"+str(user[0])+"|"+str(user[1])+"|"+str(user[2])
    decoded = b64crypt_encode(user_string)
    delete_created_token(user=int(user[0]))
    create_token(token=decoded,user=int(user[0]))

    return decoded

def decrypt_user(token:str) -> UserSerializer:
    decoded = b64crypt_decode(token).split("|")
    return UserSerializer(
        id=decoded[1],
        username=decoded[2],
        email=decoded[3]
    )

class LoginResponse(BaseModel):
    id : int 
    token : str
    username : str
    email : str

