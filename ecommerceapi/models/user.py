from pydantic import BaseModel, ConfigDict


class User(BaseModel): # esto se devuelve al cliente
    id: int | None = None
    email: str

class UserIn(User):
    password: str


