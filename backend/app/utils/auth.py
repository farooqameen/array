from fastapi import HTTPException, Request
from jose import jwt
from logger import logger


def extract_session_id(request: Request) -> str:
    """
    Extracts the session ID (sub) from the JWT token in the request cookies.

    Args:
        request (Request): The FastAPI request object containing cookies.

    Returns:
        str: The session ID extracted from the token.

    Raises:
        HTTPException: If the user is not authenticated or the token is invalid.
    """
    raw_token = request.cookies.get("idToken")
    if not raw_token:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        decoded = jwt.decode(
            raw_token,
            key="",  # Required, even when not verifying
            algorithms=["RS256"],
            options={
                "verify_signature": False,
                "verify_aud": False,  # <-- this line disables the audience check
            },
        )
        return decoded["sub"]
    except Exception as exc:
        logger.error("Token decode error: %s", exc)
        raise HTTPException(status_code=400, detail=f"Invalid token: {exc}") from exc
