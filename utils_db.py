from typing import Union
from http import HTTPStatus
from fastapi import HTTPException
from sqlalchemy import select
import database.db_orm as db

# USERS ---------------------------------------------------------------------------

def create_user(user: db.User) -> None :
    session = db.Session()
    try:
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail='No access to db, try again later')
    finally:
        session.close()
        del session

def read_user_by_username(username: str) -> Union[db.User, None]:
    session = db.Session()
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
    finally:
        session.close()
        del session

def read_user_by_username_password(username: str, password:str) -> Union[db.User, None]:
    session = db.Session()
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
    finally:
        session.close()
        del session


# PROJECTS --------------------------------------------------------------------------------------------------
def create_project(project: db.Project) -> None:
    session = db.Session()
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
    finally:
        session.close()
        del session

def validate_project_participant(project_id:int, user:db.User) -> Union[db.ProjectParticipant, None]:
    session = db.Session()
    try:
        project_participant = session.execute(
            select(db.ProjectParticipant).where(
                (db.ProjectParticipant.user_id == user.user_id) & (db.ProjectParticipant.project_id == project_id)
            )
        ).scalar_one_or_none()
        return project_participant
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later ')
    finally:
        session.close()
        del session

def read_participant_projects(user:db.User) -> list[db.Project]:
    session = db.Session()
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
    finally:
        session.close()
        del session

def read_project_by_project_name_user(project_name:str, user:db.User) -> list[db.Project]:
    session = db.Session()
    try:
        project_db = session.execute(
            select(db.Project).where(
                (db.Project.name == project_name) & (db.Project.owner == user.user_id)
            )
        ).scalar_one_or_none()
        return project_db
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
    finally:
        session.close()
        del session

def read_project_by_project_id(project_id:int, session:db.sessionmaker=None) -> Union[db.Project, None]:
    if not session: session = db.Session()
    try:
        project = session.execute(
            select(db.Project).where(
                db.Project.project_id == project_id
            )
        ).scalar_one_or_none()
        return project
    except Exception:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f'No access to db, try again later ')
    finally:
        if not session:
            session.close()
            del session

def update_project(project_id:int, project_name:str, project_description:str) -> None:
    session = db.Session()
    try:
        project_db = read_project_by_project_id(project_id, session)
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
    finally:
        session.close()
        del session

def delete_project(project_id:int, user:db.User) -> None:
    session = db.Session()
    try:
        project_db = read_project_by_project_id(project_id, session)
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
    finally:
        session.close()
        del session

# DOCUMENTS --------------------------------------------------------------------------------------------------
def create_document(document:db.Document) -> None:
    session = db.Session()
    try:
        session.add(document)
        session.commit()
        return
    except Exception:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
    finally:
        session.close()
        del session

def read_documents(project_id:int) -> Union[list[db.Document], None]:
    session = db.Session()
    try:
        documents_db = session.execute(select(db.Document).where(
            db.Document.attached_project == project_id
        )).scalars().all()
        return documents_db
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
    finally:
        session.close()
        del session

def read_document_by_id(document_id:int, session:db.sessionmaker=None) -> Union[db.Document, None]:
    if not session: session = db.Session()
    try:
        document_db = session.execute(select(db.Document).where(
            db.Document.document_id == document_id
        )).scalar_one_or_none()
        return document_db
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
    finally:
        if not session:
            session.close()
            del session

def update_document(document_id:int, document_name:str, document_file_url:str) -> None:
    session = db.Session()
    try:
        document_db = read_document_by_id(document_id, session)
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
    finally:
        session.close()
        del session

def delete_document(document_id:int, user:db.User) -> None:
    session = db.Session()
    try:
        document_db = read_document_by_id(document_id, session)
        project_db = read_project_by_project_id(document_db.attached_project, session)

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
    finally:
        session.close()
        del session