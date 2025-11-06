from abc import ABC, abstractmethod
from typing import Union
import src.db.orm as db

class UtilsDbDocument(ABC):
    @abstractmethod
    def create_document(self, document:db.Document) -> None:
        """
        Functionality to create a new document in the database.
        :param document: Document database object to be created.
        :return: None
        """
        pass

    @abstractmethod
    def read_documents(self, project_id:int) -> Union[list[db.Document], None]:
        """
        Functionality to retrieve all documents attached to a project by the project id.
        :param project_id: id of the project which owns the desired documents.
        :return: list of Document database objects or None if no documents are found.
        """
        pass

    @abstractmethod
    def read_document_by_id(self, document_id:int) -> Union[db.Document, None]:
        """
        Functionality to retrieve a document by its id.
        :param document_id: id of the document to be retrieved.
        :return: Document database object or None if no documents are found.
        """
        pass

    @abstractmethod
    def update_document(self, document_id:int, document_name:str, document_file_url:str) -> None:
        """
        Functionality to update a document by its id.
        :param document_id: id of the document to be updated.
        :param document_name: new desired name of the document.
        :param document_file_url: new desired file url of the document.
        :return: None
        """
        pass

    @abstractmethod
    def delete_document(self, document_id:int, user:db.User, project:db.Project) -> None:
        """
        Functionality to delete a document by its id.
        :param document_id: id of the document to be deleted.
        :param user: User database object to of the project owner which the document is attached to.
        :param project: Project database object of the project owner which the document is attached to.
        :return: None
        """
        pass
