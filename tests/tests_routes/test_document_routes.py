from unittest.mock import patch


import src.db.orm as db
from src.app.models import models
from src.app.routes import document_routes


class TestIntegration:

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.create_document")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.routes.document_routes.UploadFile")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_upload_project_documents(self, mock_authentication, mock_upload_file,
                                      mock_participant, mock_create_document):
        user = db.User(username="test", password="password")
        project_id = 1
        mock_upload_file.filename = "test"
        mock_upload_file.content_type = "application/test"
        documents = [mock_upload_file]
        mock_participant.return_value = True

        value = document_routes.upload_project_documents(project_id, documents, user)

        assert value == {'message': f"{len(documents)} documents successfully uploaded."}
        assert mock_create_document.called
        assert mock_participant.called

    # TODO: Add the additional test cases for upload_project_documents functionality

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_documents")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_get_project_documents(self, mock_authentication, mock_participant, mock_read_documents):
        user = db.User(username="test", password="password")
        document = db.Document(document_id=1, name="test", format="application/test",
                               file_url="../test", attached_project=1)
        project_id = 1
        mock_participant.return_value = True
        mock_read_documents.return_value = [document]

        value = document_routes.get_project_documents(project_id, user)

        assert isinstance(value, list)
        assert isinstance(value[0], models.DocumentOut)
        assert value[0].document_id == 1
        assert value[0].name == "test"
        assert value[0].format == "application/test"
        assert value[0].file_url == "../test"
        assert value[0].attached_project == 1
        assert mock_participant.called
        assert mock_read_documents.called

    # TODO: Add the additional test cases for get_project_documents functionality


    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_download_project_document(self, mock_authentication, mock_read_document, mock_participant):
        user = db.User(username="test", password="password")
        document_id = 1
        document = db.Document(document_id=1, name="test", format="application/test",
                               file_url="../test", attached_project=1)
        mock_read_document.return_value = document
        mock_participant.return_value = True

        value = document_routes.download_project_document(document_id, user)

        assert isinstance(value, models.DocumentOut)
        assert value.document_id == 1
        assert value.name == "test"
        assert value.format == "application/test"
        assert value.file_url == "../test"
        assert value.attached_project == 1
        assert mock_participant.called
        assert mock_read_document.called

    # TODO: Add the additional test cases for download_project_document functionality

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.update_document")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_update_document(self, mock_authentication, mock_read_document, mock_participant, mock_update_document):
        user = db.User(username="test", password="password")
        document_id = 1
        document = models.DocumentIn(name="test_updated", file_url='../test_updated.pdf')

        value = document_routes.update_document(document_id, document, user)

        assert value == {'message': f"{document.name} document updated successfully."}
        assert mock_participant.called
        assert mock_read_document.called
        assert mock_update_document.called

    # TODO: Add the additional test cases for update_document functionality

    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.delete_document")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.utils_db_document.utils_db_document_impl.UtilsDbDocumentImpl.read_document_by_id")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_delete_project_document(self, mock_authentication, mock_read_document, mock_read_project,
                                     mock_delete_document):
        user = db.User(username="test", password="password")
        document_id = 1

        value = document_routes.delete_project_document(document_id, user)

        assert value == {'message': f"Document deleted successfully."}
        assert mock_read_project.called
        assert mock_read_document.called
        assert mock_delete_document.called