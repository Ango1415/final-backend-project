from typing import Annotated, Union
from http import HTTPStatus
from fastapi import HTTPException, Depends, UploadFile

from src.app.utils_db.utils_db_document.utils_db_document_impl import UtilsDbDocumentImpl
from src.app.utils_db.utils_db_project.utils_db_project_impl import UtilsDbProjectImpl
from src.app.utils_db.session_singleton import SessionSingleton
from src.app.auth.auth import Authenticator
from src.app.models import models
from src.app.app import app
import src.db.orm as db

utils_db_document = UtilsDbDocumentImpl(SessionSingleton())
utils_db_project = UtilsDbProjectImpl(SessionSingleton())

@app.post("/project/{project_id}/documents")
def upload_project_documents(project_id: int, documents: list[UploadFile],
                             auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to upload documents attached to a specific project.
    :param project_id: id of the project (int) to upload documents to.
    :param documents: UploadFile object used to obtain uploaded documents, always obtained from a client form.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    if len(documents) != 0:
        is_project_participant = utils_db_project.validate_project_participant(project_id, auth_user)
        if is_project_participant:
            for document in documents:
                name = document.filename.lower().replace(' ', '_')
                file_format = document.content_type
                file_url = f'http://localhost:8000/project/{project_id}/documents/{name}'
                attached_project = project_id
                utils_db_document.create_document(
                    db.Document(name=name, format=file_format, file_url=file_url, attached_project=attached_project)
                )
            return {'message': f"{len(documents)} documents successfully uploaded."}
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="No documents were received to upload.")


@app.get("/project/{project_id}/documents")
def get_project_documents(project_id: int,
                          auth_user: Annotated[db.User, Depends(Authenticator.authentication)]
                          ) -> Union[list[models.DocumentOut], dict]:
    """
    Endpoint to get documents attached to a specific project.
    :param project_id: id of the project (int) to get documents from.
    :param auth_user: dependency injection with the process of authentication.
    :return: a list of models.Document objects attached to a specific project. if not a dict with the message of empty
    list of documents.
    """
    is_project_participant = utils_db_project.validate_project_participant(project_id, auth_user)
    if is_project_participant:
        documents_db = utils_db_document.read_documents(project_id)
        documents = []
        for document_db in documents_db:
            documents.append(models.DocumentOut(**document_db.to_dict()))
        if len(documents) > 0:
            return documents
        return {'message': f"This project doesn't have documents attached to it."}
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)


@app.get("/document/{document_id}")
def download_project_document(document_id: int,
                              auth_user: Annotated[
                                  db.User, Depends(Authenticator.authentication)]) -> models.DocumentOut:
    """
    Endpoint to download a specific document attached to a specific project.
    :param document_id: id of the document (int) to get.
    :param auth_user: dependency injection with the process of authentication.
    :return: a Document Pydantic model that contains the document to download.
    """
    document_db = utils_db_document.read_document_by_id(document_id)
    if document_db:
        is_project_participant = utils_db_project.validate_project_participant(document_db.attached_project, auth_user)
        if is_project_participant:
            return models.DocumentOut(**document_db.to_dict())
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                        detail='No document was found with that id. Try it again.')


@app.put("/document/{document_id}")
def update_document(document_id: int, document: models.DocumentIn,
                    auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to update a specific document attached to a specific project.
    :param document_id: id of the document (int) to update.
    :param document: Document pydantic model with the data needed to update the document.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    name = document.name
    url = document.file_url
    document_db = utils_db_document.read_document_by_id(document_id)
    if document_db:
        is_project_participant = utils_db_project.validate_project_participant(document_db.attached_project, auth_user)
        if is_project_participant:
            utils_db_document.update_document(document_id, name, url)
            return {'message': f"{name} document updated successfully."}
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                        detail='No document was found with that id. Try it again.')


@app.delete("/document/{document_id}")
def delete_project_document(document_id: int,
                            auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to delete a specific document attached to a specific project.
    :param document_id: id of the document (int) to delete.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    document_db = utils_db_document.read_document_by_id(document_id)
    project_db = utils_db_project.read_project_by_project_id(document_db.attached_project)
    if document_db:
        utils_db_document.delete_document(document_id, auth_user, project_db)
        return {'message': f"Document deleted successfully."}
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                        detail='No document was found with that id. Try it again.')
