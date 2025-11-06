from typing import Union
from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy import select
import src.db.orm as db
from src.app.utils_db.utils_db import UtilsDb
from src.app.utils_db.utils_db_user.utils_db_user import UtilsDbUser


class UtilsDbUserImpl(UtilsDb, UtilsDbUser):
    def create_user(self, user: db.User) -> None :
        """
        Functionality to create a new user in the database.
        :param user: User database object to be created.
        :return: None
        """
        try:
            self.session.session.add(user)
            self.session.session.commit()
            return
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail='No access to db, try again later')

    def read_user_by_username(self, username: str) -> Union[db.User, None]:
        """
        Functionality to read a user by its username from the database.
        :param username: username of the user to be read.
        :return: User database object or None if no user is found.
        """
        try:
            user = self.session.session.execute(
                select(db.User).where(
                    db.User.username == username
                )
            ).scalar_one_or_none()
            return user
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail='No access to db, try again later')

    def read_user_by_username_password(self, username: str, password:str) -> Union[db.User, None]:
        """
        Functionality to read a user by its username and its password from the database. Supports the login process.
        :param username: username of the user to be read.
        :param password: password of the user to be read.
        :return: User database object or None if no user is found.
        """
        try:
            user = self.session.session.execute(
                select(db.User).where(
                    (db.User.username == username) & (db.User.password == password)
                )
            ).scalar_one_or_none()
            return user
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f'No access to db, try again later')