from typing import Union
from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy import select
import src.db.orm as db
from src.app.utils_db.utils_db import UtilsDb
from src.app.utils_db.utils_db_project.utils_db_project import UtilsDbProject


class UtilsDbProjectImpl(UtilsDb, UtilsDbProject):
    # PROJECTS --------------------------------------------------------------------------------------------------
    def create_project(self, project: db.Project) -> None:
        """
        Functionality tp create a new project in the database.
        :param project: Project database object to be created.
        :return: None
        """
        try:
            # Create the new project in db
            self.session.session.add(project)
            self.session.session.commit()    # This commit is necessary to obtain the id of the created project in db

            # Create the new relationship in the project_participants table
            new_participant = db.ProjectParticipant(user_id=project.owner, project_id=project.project_id)
            self.session.session.add(new_participant)
            self.session.session.commit()
            return
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"ERROR - Project creation failed: 'No access to db, try again later'")

    def read_participant_projects(self, user:db.User) -> list[db.Project]:
        """
        Functionality to retrieve all projects attached to a user actively participating in them.
        :param user: User database object to be read.
        :return: list of Project database objects.
        """
        try:
            # Search for all user projects, whether they are user-owned or shared.
            participant_projects_db = self.session.session.execute(
                select(db.ProjectParticipant).where(
                    db.ProjectParticipant.user_id == user.user_id
                )
            ).scalars().all()
            projects_db = []
            for participated_project in participant_projects_db:
                projects_db.append(participated_project.project)
            return projects_db
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

    def read_project_by_project_name_user(self, project_name:str, user:db.User) -> list[db.Project]:
        """
        Functionality to retrieve a project attached to a user by the project name.
        :param project_name: name of the project which the user wants to be read.
        :param user: User database object which is doing the request.
        :return: list of Project database objects.
        """
        try:
            project_db = self.session.session.execute(
                select(db.Project).where(
                    (db.Project.name == project_name) & (db.Project.owner == user.user_id)
                )
            ).scalar_one_or_none()
            return project_db
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

    def read_project_by_project_id(self, project_id:int) -> Union[db.Project, None]:
        """
        Functionality to retrieve a project by its id.
        :param project_id: id of the project which have to be read.
        :return: Project database object or None if no project is found.
        """
        try:
            project = self.session.session.execute(
                select(db.Project).where(
                    db.Project.project_id == project_id
                )
            ).scalar_one_or_none()
            return project
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later')

    def update_project(self, project_id:int, project_name:str, project_description:str) -> None:
        """
        Functionality to update a project by its id.
        :param project_id: id of the project which have to be updated.
        :param project_name: new desired name of the project.
        :param project_description: new desired description of the project.
        :return: None
        """
        try:
            project_db = self.read_project_by_project_id(project_id)
            if project_db:
                project_db.name = project_name
                project_db.description = project_description
                self.session.session.commit()
                return
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='No project able to apply this process was found with that id. Try it again.')
        except HTTPException as http_e:
            raise http_e
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later.')

    def delete_project(self, project_id:int, user:db.User) -> None:
        """
        Functionality to delete a project by its id.
        :param project_id: id of the project which have to be deleted.
        :param user: User database object to of the project owner.
        :return: None
        """
        try:
            project_db = self.read_project_by_project_id(project_id)
            if project_db and project_db.owner == user.user_id:
                self.session.session.delete(project_db)
                self.session.session.commit()
                return
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='No project able to apply this process was found with that id. Try it again.')
        except HTTPException as http_e:
            raise http_e
        except Exception :
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later.')

    def validate_project_participant(self, project_id:int, user:db.User) -> Union[db.ProjectParticipant, None]:
        """
        Functionality to validate a project participant in the database. Supports all the authorization processes in the
        application.
        :param project_id: project id of the project which the user wants to be validated to.
        :param user: User database object to be validated.
        :return: ProjectParticipant database object to grant authorization or None if no user is found with authorization.
        """
        try:
            project_participant = self.session.session.execute(
                select(db.ProjectParticipant).where(
                    (db.ProjectParticipant.user_id == user.user_id) & (db.ProjectParticipant.project_id == project_id)
                )
            ).scalar_one_or_none()
            return project_participant
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later.')

    def create_project_participation(self, project_id:int, new_participant:db.User, user:db.User) -> None:
        """
        Functionality to create a new project participation.
        :param project_id: id of the project which the user has to be authorized.
        :param new_participant: User database object to of the new participant.
        :param user: User database object to of the project owner.
        :return:
        """
        try:
            project_db = self.read_project_by_project_id(project_id)
            if project_db.owner == user.user_id:
                participation = self.validate_project_participant(project_id, new_participant)
                if not participation:
                    #new_participation = db.ProjectParticipant(project_id=project_id, user_id=new_participant.__dict__['user_id'])
                    new_participation = db.ProjectParticipant(project_id=project_id,
                                                              user_id=new_participant.user_id)
                    self.session.session.add(new_participation)
                    self.session.session.commit()
                    return
                raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                    detail=f"The user {new_participant.username} already has participation on this project.")
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
        except HTTPException as http_e:
            raise http_e
        except Exception:
            self.session.session.rollback()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later.')
