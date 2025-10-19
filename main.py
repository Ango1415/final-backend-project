from typing import Union
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from hashlib import sha1

from sqlalchemy.exc import NoResultFound

from example_data import users, projects
import database.db_orm as db

"""
TODO: Lines 60 and 124
"""

session = db.Session() # Initialize the db (SQLAlchemy-Postgres session)
user_logged: Union[db.User, None] = None  # Simulate the user's session behavior

class User(BaseModel):
    user_id: int = None
    username: str
    password: str
    check_password: Union[str, None] = None

class Project(BaseModel):
    project_id: int = None
    name: str
    description: str = None
    owner: str = None
app = FastAPI()


@app.get("/auth")
def get_users():
    users_db = session.execute(select(db.User)).scalars().all()
    users = []
    for user_db in users_db:
        if user_db.username and user_db.password:
            user = User(user_id=user_db.user_id, username=user_db.username, password=user_db.password)
            users.append(user)
        else:
            raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Unaccessible db")
    return users

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
        try:
            usernames_db = session.execute(
                select(db.User.username).where(db.User.username == username)
            ).scalar_one_or_none()
        except Exception as error:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
        if not usernames_db:
            if password == check_password:
                # Successfully register the new account
                new_user = db.User(username=username, password=sha1(password.encode()).hexdigest())
                try:
                    session.add(new_user)
                    session.commit()
                    return {'message': f"User '{username}' successfully created!"}
                except Exception as e:
                    session.rollback()
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail=f"ERROR - User creation failed: {e}")
            else:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                    detail=f"Your password and its repetition are not the same, try it again please.")
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"Username '{username}' unavailable, try using another one")
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You must to provide proper username and password to sign up, please fill in the entire form")

@app.post("/login")
def login_service(user: User):
    username = user.username
    password = sha1(user.password.encode()).hexdigest()
    try:
        user_db = session.execute(select(db.User).where(db.User.username == username)).scalar_one_or_none()
    except Exception as error:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
    if user_db:
        if user_db.password == password:
            global user_logged
            user_logged = user_db
            return {'detail': "Logged in successfully!", 'current_user': user_logged.username}
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Incorrect username and/or password.")
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="Incorrect username and / or password.")


@app.get("/logout")
def logout_service():
    global user_logged
    if user_logged:
        user_logged = None
        return {'detail': "Successfully logged out!", 'current_user': user_logged}
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="No Session is active right now!")

@app.get("/projects")
def get_projects():
    if user_logged:
        try:
            user_projects_db = session.execute(
                select(db.Project).join(db.User).where(db.Project.owner == user_logged.user_id)
            ).scalars().all()
        except Exception as error:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
        if len(user_projects_db) == 0:
            return {'detail': "No projects were created yet!"}
        else:
            list_projects = []
            for project_db in user_projects_db:
                list_projects.append(
                    Project(
                        project_id=project_db.project_id,
                        name=project_db.name,
                        description=project_db.description,
                        owner=project_db.user.username
                    )
                )
            return list_projects
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.post("/projects")
def create_project(project: Project):
    name = project.name
    description = project.description
    if user_logged:
        if name :
            try:
                user_project = session.execute(
                    select(db.Project.name).where((db.Project.name == name) & (db.Project.owner == user_logged.user_id))
                ).scalar_one_or_none()
            except Exception as error:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
            if not user_project:
                new_project = db.Project(
                    name=name, description=description, owner=user_logged.user_id
                )
                try:
                    session.add(new_project)    # HAY QUE MANEJAR ESTO CON UN TRY-CATCH
                    session.commit()
                    return {'message': f"Project '{name}' successfully created.", 'current_user': user_logged.username}
                except Exception as e:
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                        detail=f"ERROR - Project creation failed: {e}")
            else:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                    detail=f"Project name '{name}' is currently used, changed it.")
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="Missing data, please fill in the entire form to create a new project.")
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.get("/project/{project_id}/info")
def get_project_details(project_id:int):
    if user_logged:
        try:
            user_project_db = session.execute(
                select(db.Project).join(db.User).where(
                    (db.Project.owner == user_logged.user_id) & (db.Project.project_id == project_id)
                )
            ).scalar_one_or_none()
        except Exception as error:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
        if user_project_db:
            project_info = Project(
                project_id=user_project_db.project_id,
                name=user_project_db.name,
                description=user_project_db.description,
                owner=user_project_db.user.username)
            return  project_info
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='No project was found with that id. Try it again.')
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.put("/project/{project_id}/info")
def update_project_details(project_id:str, project: Project):
    name = project.name
    description = project.description
    if user_logged:
        try:
            user_project_db = session.execute(
                select(db.Project).where((db.Project.owner == user_logged.user_id) & (db.Project.project_id == project_id))
            ).scalar_one_or_none()
        except Exception as error:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
        if user_project_db:
            user_project_db.name = name if name else user_project_db.name
            user_project_db.description = description if description else user_project_db.description
            # Esto debe ir dentro de un try-except
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"ERROR - Project update failed: {e}")

            updated_project = Project(
                project_id=user_project_db.project_id,
                name=user_project_db.name,
                description=user_project_db.description,
                owner=user_project_db.user.username
            )
            return updated_project
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='No project was found with that id. Try it again.')
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

@app.delete("/project/{project_id}")
def delete_project(project_id:str):
    if user_logged:
        try:
            user_project_db = session.execute(
                select(db.Project).where((db.Project.owner == user_logged.user_id) & (db.Project.project_id == project_id))
            ).scalar_one_or_none()
        except Exception as error:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
        if user_project_db:
            try:
                session.delete(user_project_db)
                session.commit()
                return {'message': f"Project '{project_id}' successfully deleted.", 'current_user': user_logged.username}
            except Exception as e:
                raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                    detail=f"ERROR - Project deletion failed: {e}")
        else:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail='No project was found with that id. Try it again.')
    else:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="No Session is active right now, try to log in first.")

# Endpoints to develop
"""
@app.get("/project/<project_id>/documents")
def get_project_documents(project_id:int):
    return {'message': "You're in the get_project_documents service"}

@app.post("/project/<project_id>/documents")
def upload_project_documents(project_id:int, document:dict[str, str]):
    return {'message': "You're in the upload_project_documents service"}

@app.get("/document/<document_id>")
def download_project_document(document_id:int):
    return {'message': "You're in the download_project_document service"}

@app.put("/document/<document_id>")
def update_document(document_id:int):
    return {'message': "You're in the update_document service"}

@app.delete("/document/<document_id>")
def delete_project_document(document_id:int):
    return {'message': "You're in the delete_project_document service"}

@app.post("/project/<project_id>/invite?user=<login>")
def delete_project_document(project_id:int, login:str|None):
    return {'message': "You're in the delete_project_document service"}"""