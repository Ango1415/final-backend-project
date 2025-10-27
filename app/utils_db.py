from typing import Union
from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy import select
import db.orm as db

session = db.Session()

# USERS ---------------------------------------------------------------------------
def create_user(user: db.User) -> None :
    """
    Functionality to create a new user in the database.
    :param user: User database object to be created.
    :return: None
    """
    try:
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail='No access to db, try again later')

def read_user_by_username(username: str) -> Union[db.User, None]:
    """
    Functionality to read a user by its username from the database.
    :param username: username of the user to be read.
    :return: User database object or None if no user is found.
    """
    try:
        user = session.execute(
            select(db.User).where(
                db.User.username == username
            )
        ).scalar_one_or_none()
        return user
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail='No access to db, try again later')

def read_user_by_username_password(username: str, password:str) -> Union[db.User, None]:
    """
    Functionality to read a user by its username and its password from the database. Supports the login process.
    :param username: username of the user to be read.
    :param password: password of the user to be read.
    :return: User database object or None if no user is found.
    """
    try:
        user = session.execute(
            select(db.User).where(
                (db.User.username == username) & (db.User.password == password)
            )
        ).scalar_one_or_none()
        return user
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail='No access to db, try again later')

# PROJECTS --------------------------------------------------------------------------------------------------
def create_project(project: db.Project) -> None:
    """
    Functionality tp create a new project in the database.
    :param project: Project database object to be created.
    :return: None
    """
    try:
        # Create the new project in db
        session.add(project)
        session.commit()    # This commit is necessary to obtain the id of the created project in db

        # Create the new relationship in the project_participants table
        new_participant = db.ProjectParticipant(user_id=project.owner, project_id=project.project_id)
        session.add(new_participant)
        session.commit()
        return
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail=f"ERROR - Project creation failed: 'No access to db, try again later'")

def validate_project_participant(project_id:int, user:db.User) -> Union[db.ProjectParticipant, None]:
    """
    Functionality to validate a project participant in the database. Supports all the authorization processes in the
    application.
    :param project_id: project id of the project which the user wants to be validated to.
    :param user: User database object to be validated.
    :return: ProjectParticipant database object to grant authorization or None if no user is found with authorization.
    """
    try:
        project_participant = session.execute(
            select(db.ProjectParticipant).where(
                (db.ProjectParticipant.user_id == user.user_id) & (db.ProjectParticipant.project_id == project_id)
            )
        ).scalar_one_or_none()
        return project_participant
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later ')

def read_participant_projects(user:db.User) -> list[db.Project]:
    """
    Functionality to retrieve all projects attached to a user actively participating in them.
    :param user: User database object to be read.
    :return: list of Project database objects.
    """
    try:
        # Search for all user projects, whether they are user-owned or shared.
        participant_projects_db = session.execute(
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

def read_project_by_project_name_user(project_name:str, user:db.User) -> list[db.Project]:
    """
    Functionality to retrieve a project attached to a user by the project name.
    :param project_name: name of the project which the user wants to be read.
    :param user: User database object which is doing the request.
    :return: list of Project database objects.
    """
    try:
        project_db = session.execute(
            select(db.Project).where(
                (db.Project.name == project_name) & (db.Project.owner == user.user_id)
            )
        ).scalar_one_or_none()
        return project_db
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

def read_project_by_project_id(project_id:int) -> Union[db.Project, None]:
    """
    Functionality to retrieve a project by its id.
    :param project_id: id of the project which have to be read.
    :return: Project database object or None if no project is found.
    """
    try:
        project = session.execute(
            select(db.Project).where(
                db.Project.project_id == project_id
            )
        ).scalar_one_or_none()
        return project
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later ')

def update_project(project_id:int, project_name:str, project_description:str) -> None:
    """
    Functionality to update a project by its id.
    :param project_id: id of the project which have to be updated.
    :param project_name: new desired name of the project.
    :param project_description: new desired description of the project.
    :return: None
    """
    try:
        project_db = read_project_by_project_id(project_id)
        if project_db:
            project_db.name = project_name
            project_db.description = project_description
            session.commit()
            return
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No project able to apply this process was found with that id. Try it again.')
    except HTTPException as http_e:
        raise http_e
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later')

def delete_project(project_id:int, user:db.User) -> None:
    """
    Functionality to delete a project by its id.
    :param project_id: id of the project which have to be deleted.
    :param user: User database object to of the project owner.
    :return: None
    """
    try:
        project_db = read_project_by_project_id(project_id)
        if project_db and project_db.owner == user.user_id:
            session.delete(project_db)
            session.commit()
            return
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No project able to apply this process was found with that id. Try it again.')
    except HTTPException as http_e:
        raise http_e
    except Exception :
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

# DOCUMENTS --------------------------------------------------------------------------------------------------
def create_document(document:db.Document) -> None:
    """
    Functionality to create a new document in the database.
    :param document: Document database object to be created.
    :return: None
    """
    try:
        session.add(document)
        session.commit()
        return
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

def read_documents(project_id:int) -> Union[list[db.Document], None]:
    """
    Functionality to retrieve all documents attached to a project by the project id.
    :param project_id: id of the project which owns the desired documents.
    :return: list of Document database objects or None if no documents are found.
    """
    try:
        documents_db = session.execute(select(db.Document).where(
            db.Document.attached_project == project_id
        )).scalars().all()
        return documents_db
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

def read_document_by_id(document_id:int) -> Union[db.Document, None]:
    """
    Functionality to retrieve a document by its id.
    :param document_id: id of the document to be retrieved.
    :return: Document database object or None if no documents are found.
    """
    try:
        document_db = session.execute(select(db.Document).where(
            db.Document.document_id == document_id
        )).scalar_one_or_none()
        return document_db
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

def update_document(document_id:int, document_name:str, document_file_url:str) -> None:
    """
    Functionality to update a document by its id.
    :param document_id: id of the document to be updated.
    :param document_name: new desired name of the document.
    :param document_file_url: new desired file url of the document.
    :return: None
    """
    try:
        document_db = read_document_by_id(document_id)
        if document_db:
            document_db.name = document_name
            document_db.file_url = document_file_url
            session.commit()
            return
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No project able to apply this process was found with that id. Try it again.')
    except HTTPException as http_e:
        raise http_e
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later')

def delete_document(document_id:int, user:db.User) -> None:
    """
    Functionality to delete a document by its id.
    :param document_id: id of the document to be deleted.
    :param user: User database object to of the project owner which the document is attached to.
    :return: None
    """
    try:
        document_db = read_document_by_id(document_id)
        project_db = read_project_by_project_id(document_db.__dict__['attached_project'])

        if document_db and project_db.owner == user.user_id:
            session.delete(document_db)
            session.commit()
            return
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No project able to apply this process was found with that id. Try it again.')
    except HTTPException as http_e:
        raise http_e
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

def read_project_participation(project_id:int, user:db.User) -> Union[db.Project, None]:
    """
    Functionality to retrieve a project participation by its id. Supports the authorization process.
    :param project_id: id of the project which the user has to be authorized.
    :param user: User database object of a user who the client wants to know if is authorized.
    :return: Project database object or None if the user is not authorized (no currently participating).
    """
    try:
        participation = session.execute(select(db.ProjectParticipant).where(
            (db.ProjectParticipant.project_id == project_id) & (db.ProjectParticipant.user_id == user.user_id)
        )).scalar_one_or_none()
        return participation
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,)

def create_project_participation(project_id:int, participant_username: str, user:db.User) -> None:
    """
    Functionality to create a new project participation.
    :param project_id: id of the project which the user has to be authorized.
    :param participant_username: username of the new participant.
    :param user: User database object to of the project owner.
    :return:
    """
    try:
        new_participant_db = read_user_by_username(participant_username)
        project_db = read_project_by_project_id(project_id)
        if project_db.owner == user.user_id:
            participation = read_project_participation(project_id, new_participant_db)
            if not participation:
                new_participation = db.ProjectParticipant(project_id=project_id, user_id=new_participant_db.__dict__['user_id'])
                session.add(new_participation)
                session.commit()
                return
            raise HTTPException(status_code=HTTPStatus.CONFLICT,
                                detail=f"The user {participant_username} already has participation on this project.")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        session.rollback()
        raise e
