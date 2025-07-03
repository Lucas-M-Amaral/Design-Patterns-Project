import os

from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend
)


# Authentication Configs
# ------------------------------------------------------------------------------
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
"""BearerTransport: Transport for handling JWT authentication."""

SECRET_KEY = os.getenv("SECRET_KEY")
"""str: Secret key for JWT authentication, loaded from environment variables."""


# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    """Get the JWT strategy for authentication."""
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


# Authentication Backend
auth_backend = AuthenticationBackend(
    name="Bearer",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
"""AuthenticationBackend: Backend for handling JWT authentication."""
