from typing import Annotated
from http import HTTPStatus
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
import jwt
from datetime import datetime, timedelta, timezone

from app import utils_db
import db.orm as db

# Setting for the JWT encoding.
SECRET_KEY = '-SuP3R_s3Cr3T_K3Y*'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 10

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_token(username:str) -> str:
    if ACCESS_TOKEN_EXPIRE_MINUTES:
        expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = timedelta(minutes=5)
    expire += datetime.now(timezone.utc)
    data = {'sub': username, 'exp': expire}
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return access_token

def authentication(token: Annotated[str, Depends(oauth2_scheme)]) -> db.User:
    """

    :param token:
    :return:
    """
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get('sub')
            auth_user = utils_db.read_user_by_username(username)
            if auth_user:
                return auth_user
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access (the provided username doesn't match with our system), login again.",
                headers={'WWW-Authenticate': 'Bearer'})
        except InvalidTokenError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access You must provide a valid token, login again.",
                headers={'WWW-Authenticate': 'Bearer'})
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access. You must provide a valid token, login again.",
                headers={'WWW-Authenticate': 'Bearer'})