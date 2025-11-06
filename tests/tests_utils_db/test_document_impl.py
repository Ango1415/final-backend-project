from http import HTTPStatus
from fastapi import HTTPException
from unittest.mock import patch

import pytest

from src.app.utils_db.utils_db_document.utils_db_document_impl import UtilsDbDocumentImpl

class DocumentDummy:
    def __init__(self) -> None:
        self.name = None
        self.file_url = None

class TestUnitary:

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.Document")
    def test_create_document(self, mock_document, mock_session_singleton):
        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        utils_db_document.create_document(mock_document)
        assert mock_session_singleton.session.add.called
        assert mock_session_singleton.session.commit.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.Document")
    def test_create_document_exception(self,mock_document, mock_session_singleton):
        mock_session_singleton.session.add.side_effect = Exception
        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_document.create_document(mock_document)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'
        assert mock_session_singleton.session.rollback.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_documents(self, mock_session_singleton):
        project_id = 1
        list_documents = [DocumentDummy(), DocumentDummy()]
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_scalars = mock_execute.scalars.return_value
        mock_scalars.all.return_value = list_documents

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        value = utils_db_document.read_documents(project_id)

        assert value == list_documents
        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_documents_exception(self, mock_session_singleton):
        project_id = 1
        list_documents = [DocumentDummy(), DocumentDummy()]
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_scalars = mock_execute.scalars.return_value
        mock_scalars.all.return_value = list_documents
        mock_scalars.all.side_effect = Exception

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            value = utils_db_document.read_documents(project_id)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_document_by_id(self, mock_session_singleton):
        document_id = 1
        document = DocumentDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = document

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        value = utils_db_document.read_document_by_id(document_id)

        assert isinstance(value, DocumentDummy)
        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_document_by_id_exception(self, mock_session_singleton):
        document_id = 1
        document = DocumentDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = document
        mock_execute.scalar_one_or_none.side_effect = Exception

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            value = utils_db_document.read_document_by_id(document_id)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_update_document(self, mock_session_singleton, mock_read_document):
        document_id = 1
        document_name = 'str'
        document_file_url = 'str'
        document = DocumentDummy()
        mock_read_document.return_value = document

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        utils_db_document.update_document(document_id, document_name, document_file_url)

        assert mock_session_singleton.session.commit.called
        assert document.name == document_name
        assert document.file_url == document_file_url

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_update_document_not_found(self, mock_session_singleton, mock_read_document):
        document_id = 1
        document_name = 'str'
        document_file_url = 'str'
        document = DocumentDummy()
        mock_read_document.return_value = None

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_document.update_document(document_id, document_name, document_file_url)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.NOT_FOUND
        assert expected.value.detail == 'No project able to apply this process was found with that id. Try it again.'

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_update_document_exception(self, mock_session_singleton, mock_read_document):
        document_id = 1
        document_name = 'str'
        document_file_url = 'str'
        document = DocumentDummy()
        mock_read_document.return_value = document
        mock_read_document.side_effect = Exception

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_document.update_document(document_id, document_name, document_file_url)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'
        assert mock_session_singleton.session.rollback.called

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.Project")
    @patch("src.db.orm.User")
    def test_delete_document(self, mock_user, mock_project, mock_session_singleton, mock_read_document):
        document_id = 1
        user_id = 2
        document = DocumentDummy()

        mock_user.user_id = user_id
        mock_project.owner = user_id
        mock_read_document.return_value = document

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        utils_db_document.delete_document(document_id, mock_user, mock_project)

        assert mock_session_singleton.session.commit.called
        assert mock_session_singleton.session.delete.called

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.Project")
    @patch("src.db.orm.User")
    def test_delete_document_not_found(self, mock_user, mock_project, mock_session_singleton, mock_read_document):
        document_id = 1
        user_id = 2

        mock_user.user_id = user_id
        mock_project.owner = user_id
        mock_read_document.return_value = None

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_document.delete_document(document_id, mock_user, mock_project)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.NOT_FOUND
        assert expected.value.detail == 'No project able to apply this process was found with that id. Try it again.'

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.Project")
    @patch("src.db.orm.User")
    def test_delete_document_exception(self, mock_user, mock_project, mock_session_singleton, mock_read_document):
        document_id = 1
        user_id = 2

        mock_user.user_id = user_id
        mock_project.owner = user_id
        mock_read_document.return_value = None
        mock_read_document.side_effect = Exception

        utils_db_document = UtilsDbDocumentImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_document.delete_document(document_id, mock_user, mock_project)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'
        assert mock_session_singleton.session.rollback.called
