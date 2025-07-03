from fastapi import Request, HTTPException
from src.logs import logger
from src.common.utils import get_aws_session_w_region
from src.settings import settings
secrets_manager_session = get_aws_session_w_region()
client = secrets_manager_session.client('cognito-idp')


async def auth(request: Request) -> None:
    """
    Authenticate the incoming request based on environment settings.

    In PROD or DEV environments, validates a session token via Cognito.
    In local environments, validates an API key.

    Args:
        request (Request): The incoming HTTP request.

    Raises:
        HTTPException: If authentication fails with a 403 Unauthorized status.
    """
    # If in PROD or DEV, validate session token 
    if (settings.env == 'PROD' or settings.env == 'DEV'):
        logger.info(f"environment is {settings.env}")
        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            logger.error("Unauthorized. No Session Token found.")
            raise HTTPException(status_code=403, detail="Unauthorized.")

        token = auth_header.split(" ")[1]
        await verify_token(token)
    else:
        # else (not specified, assuming local), validate api key  
        key = request.headers.get("APIAuth")
        if not key:
            logger.error("Unauthorized. No API Key found.")
            raise HTTPException(status_code=403, detail="Unauthorized.")

        if not (settings.api_auth_key == key):
            logger.error("Unauthorized. Incorrect API Key.")
            raise HTTPException(status_code=403, detail="Unauthorized.")        


async def verify_token(token:str) -> None:
    """
    Verify the authentication token using AWS Cognito.

    Args:
        token (str): The authentication token to verify.

    Raises:
        HTTPException: If token verification fails with a 403 Unauthorized status.
    """
    try:
        client.get_user(AccessToken=token)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="Unauthorized")
    
