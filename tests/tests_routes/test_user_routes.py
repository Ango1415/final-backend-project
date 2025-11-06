from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi import HTTPException

import src.app.routes.user_routes as user_routes
from src.app.models import models
import src.db.orm as db

class TestIntegration:

    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.create_user")
    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username")
    def test_create_user(self, mock_read_user, mock_create_user):
        mock_read_user.return_value = None
        user = models.UserIn(username="test", password="password", check_password="password")
        value = user_routes.create_user(user)

        assert mock_read_user.called
        assert mock_create_user.called
        assert isinstance(value, dict)
        assert value['message'] == f"User '{user.username}' successfully created!"

    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.create_user")
    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username")
    def test_create_user_bad_request_wrong_password(self, mock_read_user, mock_create_user):
        mock_read_user.return_value = None
        user = models.UserIn(username="test", password="password", check_password="different")
        with pytest.raises(HTTPException) as expected:
            user_routes.create_user(user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.BAD_REQUEST
        assert expected.value.detail == f"Your password and its repetition don't match, try it again please."

    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.create_user")
    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username")
    def test_create_user_bad_request_existent_user(self, mock_read_user, mock_create_user):
        user = models.UserIn(username="test", password="password", check_password="different")
        with pytest.raises(HTTPException) as expected:
            user_routes.create_user(user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.BAD_REQUEST
        assert expected.value.detail == f"Username '{user.username}' already in use, try using another one"

    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username_password")
    @patch("src.app.routes.user_routes.OAuth2PasswordRequestForm")
    def test_login_service(self, mock_form_data, mock_read_user_password):
        user = db.User(username="test", password="password")
        mock_read_user_password.return_value = user
        mock_form_data.username = "test"
        mock_form_data.password = "password"

        value = user_routes.login_service(mock_form_data)
        assert mock_read_user_password.called
        assert isinstance(value, models.Token)
        assert value.access_token
        assert value.token_type == 'bearer'

    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username_password")
    @patch("src.app.routes.user_routes.OAuth2PasswordRequestForm")
    def test_login_service_unauthorized(self, mock_form_data, mock_read_user_password):
        user = db.User(username="test", password="password")
        mock_read_user_password.return_value = None
        mock_form_data.username = "test"
        mock_form_data.password = "password"

        with pytest.raises(HTTPException) as expected:
            value = user_routes.login_service(mock_form_data)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.UNAUTHORIZED
        assert expected.value.detail == "Incorrect username and / or password."
        assert expected.value.headers == {"WWW-Authenticate": "Bearer"}

    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username_password")
    @patch("src.app.routes.user_routes.OAuth2PasswordRequestForm")
    def test_login_service_bad_request(self, mock_form_data, mock_read_user_password):
        user = db.User(username="test", password="password")
        mock_read_user_password.return_value = user
        mock_form_data.username = None
        mock_form_data.password = "password"

        with pytest.raises(HTTPException) as expected:
            value = user_routes.login_service(mock_form_data)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.BAD_REQUEST
        assert expected.value.detail == "Missing data, please fill in the entire form."
