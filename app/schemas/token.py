from pydantic import BaseModel, Field

from app.schemas.user import User


class Token(BaseModel):
    """Token pair returned on login, register or refresh."""

    access_token: str = Field(..., description="Short-lived token sent on every request.")
    refresh_token: str = Field(..., description="Long-lived token used to get new access tokens.")


class LoginResponse(BaseModel):
    """Response returned on login and register — tokens plus user profile."""

    access_token: str
    refresh_token: str
    user: User


class TokenRefresh(BaseModel):
    """Body for exchanging a refresh token for a new token pair."""

    refresh_token: str


class LoginPayload(BaseModel):
    """Body for logging in."""

    email: str
    password: str
