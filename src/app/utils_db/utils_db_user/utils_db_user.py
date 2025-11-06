from abc import ABC, abstractmethod
from typing import Union

import src.db.orm as db

class UtilsDbUser(ABC):
    @abstractmethod
    def create_user(self, user: db.User) -> None :
        """
        Functionality to create a new user in the database.
        :param user: User database object to be created.
        :return: None
        """
        pass

    @abstractmethod
    def read_user_by_username(self, username: str) -> Union[db.User, None]:
        """
        Functionality to read a user by its username from the database.
        :param username: username of the user to be read.
        :return: User database object or None if no user is found.
        """
        pass

    @abstractmethod
    def read_user_by_username_password(self, username: str, password:str) -> Union[db.User, None]:
        """
        Functionality to read a user by its username and its password from the database. Supports the login process.
        :param username: username of the user to be read.
        :param password: password of the user to be read.
        :return: User database object or None if no user is found.
        """
        pass