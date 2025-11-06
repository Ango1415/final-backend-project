from abc import ABC, abstractmethod
from typing import Union

import src.db.orm as db



class UtilsDbProject(ABC):
    @abstractmethod
    def create_project(self, project: db.Project) -> None:
        """
        Functionality tp create a new project in the database.
        :param project: Project database object to be created.
        :return: None
        """
        pass

    @abstractmethod
    def read_participant_projects(self, user:db.User) -> list[db.Project]:
        """
        Functionality to retrieve all projects attached to a user actively participating in them.
        :param user: User database object to be read.
        :return: list of Project database objects.
        """
        pass

    @abstractmethod
    def read_project_by_project_name_user(self, project_name:str, user:db.User) -> list[db.Project]:
        """
        Functionality to retrieve a project attached to a user by the project name.
        :param project_name: name of the project which the user wants to be read.
        :param user: User database object which is doing the request.
        :return: list of Project database objects.
        """
        pass

    @abstractmethod
    def read_project_by_project_id(self, project_id:int) -> Union[db.Project, None]:
        """
        Functionality to retrieve a project by its id.
        :param project_id: id of the project which have to be read.
        :return: Project database object or None if no project is found.
        """
        pass

    @abstractmethod
    def update_project(self, project_id:int, project_name:str, project_description:str) -> None:
        """
        Functionality to update a project by its id.
        :param project_id: id of the project which have to be updated.
        :param project_name: new desired name of the project.
        :param project_description: new desired description of the project.
        :return: None
        """
        pass

    @abstractmethod
    def delete_project(self, project_id:int, user:db.User) -> None:
        """
        Functionality to delete a project by its id.
        :param project_id: id of the project which have to be deleted.
        :param user: User database object to of the project owner.
        :return: None
        """
        pass

    @abstractmethod
    def validate_project_participant(self, project_id: int, user: db.User) -> Union[db.ProjectParticipant, None]:
        """
        Functionality to validate a project participant in the database. Supports all the authorization processes in the
        application.
        :param project_id: project id of the project which the user wants to be validated to.
        :param user: User database object to be validated.
        :return: ProjectParticipant database object to grant authorization or None if no user is found with authorization.
        """
        pass

    @abstractmethod
    def create_project_participation(self, project_id:int, new_participant:db.User, user:db.User) -> None:
        """
        Functionality to create a new project participation.
        :param project_id: id of the project which the user has to be authorized.
        :param new_participant: User database object to of the new participant.
        :param user: User database object to of the project owner.
        :return:
        """
        pass