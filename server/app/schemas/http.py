from pydantic import BaseModel


class AuthRequest(BaseModel):
    login: str
    password: str


class UserAuthResponse(BaseModel):
    login: str
