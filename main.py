from datetime import datetime, timedelta, timezone
from typing import Union, Annotated
from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import select
from hashlib import sha1
from jwt.exceptions import InvalidTokenError
import jwt

import database.db_orm as db

# Setting for the JWT encoding.
SECRET_KEY = '-SuP3R_s3Cr3T_K3Y*'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 6

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

class User(BaseModel):
    user_id: int = None
    username: str =  Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=100)
    check_password: Union[str, None] = None

class Project(BaseModel):
    project_id: Union[int, None] = None
    name: str = Field(min_length=1, max_length=50)
    description: Union[str, None] = Field(min_length=0, max_length=200)
    owner: Union[str, None] = None

class Document(BaseModel):
    document_id: Union[int, None] = None
    name: str = Field(min_length=1, max_length=50)
    format: str = Field(min_length=0, max_length=100)
    file_url: str = Field(min_length=1, max_length=200)
    attached_project: Union[str, None] = None

class Token(BaseModel):
    access_token: str = Field(min_length=1, max_length=200)
    token_type: str = "bearer"
    username: Union[str, None] =  None



def authentication(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    if token:
        session = db.Session()  # Initialize the db (SQLAlchemy-Postgres session)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get('sub')
            try:
                auth_user = session.execute(select(db.User).where(
                    db.User.username == username
                )).scalar_one_or_none()
            except Exception :
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                    detail='No access to db, try again later')
            if auth_user:
                return User(user_id=auth_user.user_id, username=auth_user.username, password=auth_user.password)
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access, login again.",
                headers={'WWW-Authenticate': 'Bearer'})
        except InvalidTokenError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access, login again.",
                headers={'WWW-Authenticate': 'Bearer'})
        finally:
            session.close()
            del session
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access, login again.",
                headers={'WWW-Authenticate': 'Bearer'})


app = FastAPI()


@app.get("/auth")
def get_users():
    session = db.Session()  # Initialize the db (SQLAlchemy-Postgres session)
    try:
        users_db = session.execute(select(db.User)).scalars().all()
        users = []
        for user_db in users_db:
            if user_db.username and user_db.password:
                user = User(user_id=user_db.user_id, username=user_db.username, password=user_db.password)
                users.append(user)
            else:
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Unaccessible db")
        return users
    except Exception as e:
        raise e
    finally:
        session.close()
        del session

# Project requirements
@app.post("/auth")
def create_user(user: User):
    """
    Allows the creation of users into the system
    :param user: Account username and password (JSON)
    :return: dict with a message related to the process done
    """
    username = user.username
    password = user.password
    check_password = user.check_password

    if username and password and check_password:    #Checks if the user provides the entire info needed for the process
        session = db.Session()  # Initialize the db (SQLAlchemy-Postgres session)
        try:
            try:
                usernames_db = session.execute(
                    select(db.User.username).where(db.User.username == username)
                ).scalar_one_or_none()
            except Exception :
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
            if not usernames_db:
                if password == check_password:
                    # Successfully register the new account
                    new_user = db.User(username=username, password=sha1(password.encode()).hexdigest())
                    try:
                        session.add(new_user)
                        session.commit()
                        return {'message': f"User '{username}' successfully created!"}
                    except Exception :
                        session.rollback()
                        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                            detail=f"ERROR - User creation failed: 'No access to db, try again later'")
                else:
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail=f"Your password and its repetition are not the same, try it again please.")
            else:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                    detail=f"Username '{username}' unavailable, try using another one")
        except Exception as e:
            raise e
        finally:
            session.close()
            del session
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You must to provide proper username and password to sign up, please fill in the entire form")

@app.post("/login")
def login_service(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if form_data.username and form_data.password:
        username = form_data.username
        password = sha1(form_data.password.encode()).hexdigest()

        session = db.Session()  # Initialize the db (SQLAlchemy-Postgres session)
        try:
            user_db = session.execute(select(db.User).where(
                (db.User.username == username) & (db.User.password == password)
            )).scalar_one_or_none()
        except Exception :
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail='No access to db, try again later')
        finally:
            session.close()
            del session
        if user_db:
            if ACCESS_TOKEN_EXPIRE_MINUTES:
                expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            else:
                expire = timedelta(minutes=5)
            expire += datetime.now(timezone.utc)
            data = {'sub': user_db.username, 'exp': expire}
            access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
            return Token(access_token=access_token)

        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect username and / or password.",
                            headers={'WWW-Authenticate': 'Bearer'})
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="Missing data, please fill in the entire form.")

@app.get("/projects")
def get_projects(auth_user: Annotated[User, Depends(authentication)]):
    if auth_user:
        session = db.Session()  # Initialize the db (SQLAlchemy-Postgres session)
        try:
            try:
                projects_db = session.execute(
                    select(db.ProjectParticipant).where(db.ProjectParticipant.user_id == auth_user.user_id)
                ).scalars().all()
            except Exception :
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

            if len(projects_db) == 0:
                return {'detail': "No projects were created (or have access) yet!"}
            else:
                list_projects = []
                for project_db in projects_db:
                    list_projects.append(
                        Project(
                            project_id=project_db.project_id,
                            name=project_db.project.name,
                            description=project_db.project.description,
                            owner=project_db.project.user.username
                        )
                    )
                return list_projects
        except Exception as e:
            raise e
        finally:
            session.close()
            del session
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.",
                            headers={"WWW-Authenticate": "Bearer"})

@app.post("/projects")
def create_project(project: Project,
                   auth_user: Annotated[User, Depends(authentication)]):
    name = project.name
    description = project.description
    if auth_user:
        if name :
            session = db.Session()  # Initialize the db (SQLAlchemy-Postgres session)
            try:
                try:
                    project_db = session.execute(
                        select(db.Project.name).where((db.Project.name == name) & (db.Project.owner == auth_user.user_id))
                    ).scalar_one_or_none()
                except Exception :
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

                if not project_db:
                    new_project = db.Project(name=name, description=description, owner=auth_user.user_id)
                    try:
                        session.add(new_project)
                        session.commit()

                        new_project_db_id = session.execute(
                            select(db.Project.project_id).where(
                                (db.Project.name == name) & (db.Project.owner == auth_user.user_id))
                        ).scalar_one_or_none()

                        new_participant = db.ProjectParticipant(user_id=auth_user.user_id, project_id=new_project_db_id)

                        session.add(new_participant)
                        session.commit()

                        return {'message': f"Project '{name}' successfully created.", 'current_user': auth_user.username}

                    except Exception :
                        session.rollback()
                        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                            detail=f"ERROR - Project creation failed: 'No access to db, try again later'")
                else:
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail=f"Project name '{name}' is currently used, changed it.")
            except Exception as e:
                raise e
            finally:
                session.close()
                del session
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Missing data, please fill in the entire form to create a new project.")
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.get("/project/{project_id}/info")
def get_project_details(project_id:int,
                        auth_user: Annotated[User, Depends(authentication)]):
    if auth_user:
        session = db.Session()
        try:
            try:
                desired_project_db = session.execute(
                    select(db.ProjectParticipant).where(
                        (db.ProjectParticipant.user_id == auth_user.user_id) &
                        (db.ProjectParticipant.project_id == project_id)
                    )
                ).scalar_one_or_none()
            except Exception :
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
            if desired_project_db:
                project_info = Project(
                    project_id=desired_project_db.project_id,
                    name=desired_project_db.project.name,
                    description=desired_project_db.project.description,
                    owner=desired_project_db.project.user.username)
                return  project_info
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                    detail='No project was found with that id. Try it again.')
        except Exception as e:
            raise e
        finally:
            session.close()
            del session
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.put("/project/{project_id}/info")
def update_project_details(project_id:str, project: Project,
                           auth_user: Annotated[User, Depends(authentication)]):
    name = project.name
    description = project.description
    if auth_user:
        session = db.Session()
        try:
            try:
                project_db = session.execute(
                    select(db.ProjectParticipant).where(
                        (db.ProjectParticipant.user_id == auth_user.user_id) &
                        (db.ProjectParticipant.project_id == project_id)
                    )
                ).scalar_one_or_none()
            except Exception :
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
            if project_db:
                project_db.project.name = name if name else project_db.project.name
                project_db.project.description = description if description else project_db.project.description
                try:
                    session.commit()
                except Exception :
                    session.rollback()
                    raise HTTPException(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        detail=f"ERROR - Project update failed: 'No access to db, try again later'")

                updated_project = Project(
                    project_id=project_db.project.project_id,
                    name=project_db.project.name,
                    description=project_db.project.description,
                    owner=project_db.project.user.username
                )
                return updated_project
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                    detail='No project was found with that id. Try it again.')
        except Exception as e:
            raise e
        finally:
            session.close()
            del session
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.delete("/project/{project_id}")
def delete_project(project_id:str,
                   auth_user: Annotated[User, Depends(authentication)]):
    if auth_user:
        session = db.Session()
        try:
            try:
                user_project_db = session.execute(
                    select(db.Project).where((db.Project.owner == auth_user.user_id) & (db.Project.project_id == project_id))
                ).scalar_one_or_none()
            except Exception:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')

            if user_project_db:
                try:
                    session.delete(user_project_db)
                    session.commit()
                    return {'message': f"Project '{project_id}' successfully deleted.", 'current_user': auth_user.username}
                except Exception:
                    session.rollback()
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail=f"ERROR - Project deletion failed: 'No access to db, try again later'")
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                    detail='No project was found with that id. Try it again.')
        except Exception as e:
            raise e
        finally:
            session.close()
            del session
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.post("/project/{project_id}/documents")
def upload_project_documents(project_id:int, documents:list[UploadFile],
                             auth_user: Annotated[User, Depends(authentication)]):
    if len(documents) != 0:
        session = db.Session()
        try:
            try:
                desired_project_db = session.execute(
                    select(db.ProjectParticipant.project_id).where(
                        (db.ProjectParticipant.user_id == auth_user.user_id) &
                        (db.ProjectParticipant.project_id == project_id)
                    )
                ).scalar_one_or_none()
            except Exception :
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No access to db, try again later')
            if desired_project_db:
                try:
                    for document in documents:
                        new_document_db = db.Document(
                            name=document.filename,
                            format=document.content_type,
                            file_url=f'http://localhost:8000/project/{project_id}/documents/{document.filename}',
                            attached_project=desired_project_db.project_id
                        )
                        session.add(new_document_db)
                    session.commit()
                    return {'message': f"{len(documents)} documents successfully uploaded."}
                except Exception :
                    session.rollback()
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail='No access to db, try again later')
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                    detail='No project was found with that id. Try it again.')
        except Exception as e:
            raise e
        finally:
            session.close()
            del session
    return {'message': "No documents were received to upload."}

@app.get("/project/{project_id}/documents")
def get_project_documents(project_id:int,
                          auth_user: Annotated[User, Depends(authentication)]):
    session = db.Session()
    try:
        try:
            desired_project_db = session.execute(
                select(db.ProjectParticipant).where(
                    (db.ProjectParticipant.user_id == auth_user.user_id) &
                    (db.ProjectParticipant.project_id == project_id)
                )
            ).scalar_one_or_none()
        except Exception:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='No accessible project, try it again.')
        if desired_project_db:
            try:
                documents_db = desired_project_db.project.documents
                if len(documents_db) != 0:
                    documents = []
                    for document_db in documents_db:
                        new_document = Document(
                            document_id=document_db.document_id,
                            name=document_db.name,
                            format=document_db.format,
                            file_url=document_db.file_url,
                            attached_project=str(desired_project_db.project_id)
                        )
                        documents.append(new_document)
                    return documents
                return {'message': "No documents are attached to this project."}
            except Exception as e:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                    detail=f'There was a problem with the documents, try again: {e}')
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='No project was found with that id. Try it again.')
    except Exception as e:
        raise e
    finally:
        session.close()
        del session

@app.get("/document/{document_id}")
def download_project_document(document_id:int,
                              auth_user: Annotated[User, Depends(authentication)]):
    session = db.Session()
    try:
        document_db = session.execute(
            select(db.Document).where(
                (db.Document.document_id == document_id)
            )
        ).scalar_one_or_none()
        if document_db:
            is_authorized = session.execute(
                select(db.ProjectParticipant.project_id).where(
                    (db.ProjectParticipant.user_id == auth_user.user_id) & (db.ProjectParticipant.project_id == document_db.attached_project)
                )
            ).scalar_one_or_none()
            if is_authorized:
                return Document(
                    document_id=document_db.document_id,
                    name=document_db.name,
                    format=document_db.format,
                    file_url=document_db.file_url,
                    attached_project=str(document_db.attached_project)
                )
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail="You don't have access to this document.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No document was found with that id. Try it again.')
    except Exception as e:
        raise e
    finally:
        session.close()
        del session

@app.put("/document/{document_id}")
def update_document(document_id:int, document:Document,
                    auth_user: Annotated[User, Depends(authentication)]):
    session = db.Session()
    try:
        document_db = session.execute(
            select(db.Document).where(
                (db.Document.document_id == document_id)
            )
        ).scalar_one_or_none()
        if document_db:
            is_authorized = session.execute(
                select(db.ProjectParticipant.project_id).where(
                    (db.ProjectParticipant.user_id == auth_user.user_id) & (
                                db.ProjectParticipant.project_id == document_db.attached_project)
                )
            ).scalar_one_or_none()
            if is_authorized:
                try:
                    document_db.name = document.name if document.name else document_db.name
                    document_db.format = document.format if document.format else document_db.format
                    document_db.file_url = document.file_url if document.file_url else document_db.file_url
                    session.commit()
                    return {'message': 'Document updated successfully.'}
                except Exception:
                    session.rollback()
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail='There was a problem updating the document, try again.')
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail="You don't have access to this document.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No document was found with that id. Try it again.')
    except Exception as e:
        raise e
    finally:
        session.close()
        del session

@app.delete("/document/{document_id}")
def delete_project_document(document_id:int,
                            auth_user: Annotated[User, Depends(authentication)]):
    session = db.Session()
    try:
        document_db = session.execute(
            select(db.Document).where(
                (db.Document.document_id == document_id)
            )
        ).scalar_one_or_none()
        if document_db:
            if document_db.project.owner == auth_user.user_id:
                try:
                    session.delete(document_db)
                    session.commit()
                    return {'message': 'Document deleted successfully.'}
                except Exception:
                    session.rollback()
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail='There was a problem updating the document, try again.')
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail="You don't have access to this document.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='No document was found with that id. Try it again.')
    except Exception as e:
        raise e
    finally:
        session.close()
        del session

# Endpoints to develop
"""
@app.post("/project/<project_id>/invite?user=<login>")
def delete_project_document(project_id:int, login:str|None):
    return {'message': "You're in the delete_project_document service"}"""