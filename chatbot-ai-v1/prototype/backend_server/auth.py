import os
from fastapi import Request, HTTPException
import logging
from common.utils import Credential, validate_credential
import boto3

client = boto3.client('cognito-idp')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] {%(module)s::%(funcName)s} %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("backend_server")

async def auth(request: Request):
    # If in PROD or DEV, validate session token 
    if ("ENV" in os.environ and (os.environ.get('ENV') == 'PROD' or os.environ.get('ENV') == 'DEV')):
        logger.info(f"environment is {os.environ.get('ENV')}")
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

        if not ("API_AUTH_KEY" in os.environ and os.environ.get('API_AUTH_KEY') == key):
            logger.error("Unauthorized. Incorrect API Key.")
            raise HTTPException(status_code=403, detail="Unauthorized.")        


async def verify_token(token):
    try:
        client.get_user(AccessToken=token)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="Unauthorized")
    
