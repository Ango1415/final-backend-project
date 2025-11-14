from typing import Annotated
from http import HTTPStatus
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from hashlib import sha1

from src.app.utils_db.utils_db_user.utils_db_user_impl import UtilsDbUserImpl
from src.app.utils_db.session_singleton import SessionSingleton
from src.app.auth.auth import Authenticator
import src.app.models.models as models
from src.app.app import app
import src.db.orm as db

utils_db_user = UtilsDbUserImpl(SessionSingleton())
@app.post("/auth")
def create_user(user: models.UserIn) -> dict[str, str]:
    """
    Endpoint to create a new user in the app.
    :param user: Pydantic User model (JSON) used to receive the data needed to create a new user.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    username = user.username
    password = user.password
    check_password = user.check_password
    if username and password and check_password:
        username_db = utils_db_user.read_user_by_username(username)
        if not username_db:
            if password == check_password:
                new_user = db.User(username=username, password=sha1(password.encode()).hexdigest())
                utils_db_user.create_user(new_user)
                return {'message': f"User '{user.username}' successfully created!"}
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"Your password and its repetition don't match, try it again please.")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Username '{username}' already in use, try using another one")
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You must to provide proper username and password to sign up, please fill in the entire form")

@app.post("/login")
def login_service(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.Token:
    """
    Endpoint to provide the login service in the app.
    :param form_data: Form data received from the client.
    :return: Token pydantic model if login was successful.
    """
    username = form_data.username
    password = sha1(form_data.password.encode()).hexdigest()
    if username and password:
        user_db = utils_db_user.read_user_by_username_password(username, password)
        if user_db:
            access_token = Authenticator.create_token(username=user_db.username)
            return models.Token(access_token=access_token, token_type='bearer')
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect username and / or password.",
                            headers={'WWW-Authenticate': 'Bearer'})
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="Missing data, please fill in the entire form.")