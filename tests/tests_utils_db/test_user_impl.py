import pytest
from http import HTTPStatus
from unittest.mock import patch

from fastapi import HTTPException

from src.app.utils_db.utils_db_user.utils_db_user_impl import UtilsDbUserImpl

class TestUnitary:

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_create_user(self, mock_user_db, mock_session_singleton):
        #mock_session_singleton.session.add.return_value = None
        #mock_session_singleton.session.commit.return_value = None

        utils_db_user = UtilsDbUserImpl(mock_session_singleton)
        user = mock_user_db
        utils_db_user.create_user(user)

        assert mock_session_singleton.session.add.called
        assert mock_session_singleton.session.commit.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_create_user_exception(self, mock_user_db, mock_session_singleton):
        #mock_session_singleton.session.add.return_value = None
        mock_session_singleton.session.add.side_effect = HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='No access to db, try again later'
        )
        #mock_session_singleton.session.commit.return_value = None

        utils_db_user = UtilsDbUserImpl(mock_session_singleton)
        user = mock_user_db
        with pytest.raises(HTTPException) as expected:
            utils_db_user.create_user(user)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_user_by_username(self, mock_session_singleton):
        #mock_session_singleton.session.execute = MagicMock(SessionSingleton().session.execute)
        username = "test"

        utils_db_user = UtilsDbUserImpl(mock_session_singleton)
        value = utils_db_user.read_user_by_username(username)

        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_user_by_username_exception(self, mock_session_singleton):
        #mock_session_singleton.session.execute = MagicMock(SessionSingleton().session.execute)
        mock_session_singleton.session.execute.side_effect = Exception
        username = "test"

        utils_db_user = UtilsDbUserImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            value = utils_db_user.read_user_by_username(username)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_user_by_username_password(self, mock_session_singleton):
        #mock_session_singleton.session.execute = MagicMock(SessionSingleton().session.execute)
        username = "test"
        password = "password"
        utils_db_user = UtilsDbUserImpl(mock_session_singleton)
        utils_db_user.read_user_by_username_password(username, password)
        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_user_by_username_password_exception(self, mock_session_singleton):
        #mock_session_singleton.session.execute = MagicMock(SessionSingleton().session.execute)
        mock_session_singleton.session.execute.side_effect = Exception
        username = "test"
        password = "password"
        utils_db_user = UtilsDbUserImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_user.read_user_by_username_password(username, password)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'


