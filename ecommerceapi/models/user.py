from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None = None
    email: str


class UserIn(User):
    password: str
