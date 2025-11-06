from typing import Union
from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy import select

from src.app.utils_db.utils_db_document.utils_db_document import UtilsDbDocument
from src.app.utils_db.utils_db import UtilsDb
import src.db.orm as db


class UtilsDbDocumentImpl(UtilsDb, UtilsDbDocument):

    def create_document(self, document:db.Document) -> None:
        """
        Functionality to create a new document in the database.
        :param document: Document database object to be created.
        :return: None
        """
        try:
            self.session.session.add(document)
            self.session.session.commit()
            return
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later.')

    def read_documents(self, project_id:int) -> Union[list[db.Document], None]:
        """
        Functionality to retrieve all documents attached to a project by the project id.
        :param project_id: id of the project which owns the desired documents.
        :return: list of Document database objects or None if no documents are found.
        """
        try:
            documents_db = self.session.session.execute(select(db.Document).where(
                db.Document.attached_project == project_id
            )).scalars().all()
            return documents_db
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later.')

    def read_document_by_id(self, document_id:int) -> Union[db.Document, None]:
        """
        Functionality to retrieve a document by its id.
        :param document_id: id of the document to be retrieved.
        :return: Document database object or None if no documents are found.
        """
        try:
            document_db = self.session.session.execute(select(db.Document).where(
                db.Document.document_id == document_id
            )).scalar_one_or_none()
            return document_db
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later.')

    def update_document(self, document_id:int, document_name:str, document_file_url:str) -> None:
        """
        Functionality to update a document by its id.
        :param document_id: id of the document to be updated.
        :param document_name: new desired name of the document.
        :param document_file_url: new desired file url of the document.
        :return: None
        """
        try:
            document_db = self.read_document_by_id(document_id)
            if document_db:
                document_db.name = document_name
                document_db.file_url = document_file_url
                self.session.session.commit()
                return
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='No project able to apply this process was found with that id. Try it again.')
        except HTTPException as http_e:
            raise http_e
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later.')

    def delete_document(self, document_id:int, user:db.User, project:db.Project) -> None:
        """
        Functionality to delete a document by its id.
        :param document_id: id of the document to be deleted.
        :param user: User database object of the project owner which the document is attached to.
        :param project: Project database object of the project owner which the document is attached to.
        :return: None
        """
        try:
            document_db = self.read_document_by_id(document_id)
            if document_db and project.owner == user.user_id:
                self.session.session.delete(document_db)
                self.session.session.commit()
                return
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='No project able to apply this process was found with that id. Try it again.')
        except HTTPException as http_e:
            raise http_e
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
