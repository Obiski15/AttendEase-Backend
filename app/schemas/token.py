from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token pair returned on login, register or refresh."""

    access_token: str = Field(..., description="Short-lived token sent on every request.")
    refresh_token: str = Field(..., description="Long-lived token used to get new access tokens.")
    token_type: str = Field(default="bearer", description="Always 'bearer'.")


class TokenRefresh(BaseModel):
    """Body for exchanging a refresh token for a new token pair."""

    refresh_token: str


class LoginPayload(BaseModel):
    """Body for logging in."""
    
    email: str
    password: str
