from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
