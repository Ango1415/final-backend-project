from typing import Annotated, Union
from http import HTTPStatus
from fastapi import HTTPException, Depends

from src.app.utils_db.utils_db_project.utils_db_project_impl import UtilsDbProjectImpl
from src.app.utils_db.utils_db_user.utils_db_user_impl import UtilsDbUserImpl
from src.app.utils_db.session_singleton import SessionSingleton
from src.app.auth.auth import Authenticator
from src.app.models import models
from src.app.app import app
import src.db.orm as db

utils_db_project = UtilsDbProjectImpl(SessionSingleton())
utils_db_user = UtilsDbUserImpl(SessionSingleton())

@app.get("/projects")
def get_projects(auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> Union[list[
    models.ProjectOut], dict]:
    """
    Endpoint to retrieve all projects attached to a user (from his property or shared) in the app.
    :param auth_user: dependency injection with the process of authentication.
    :return: list of projects attached to a user.
    """
    projects_db = utils_db_project.read_participant_projects(auth_user)
    if len(projects_db) != 0:
        projects = []
        for project_db in projects_db:
            projects.append(
                models.ProjectOut(**project_db.to_dict())
            )
        return projects
    return {'detail': "No projects were created (or have access) yet!"}

@app.post("/projects")
def create_project(project: models.ProjectIn,
                   auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to create a new project in the app.
    :param project: Project model (JSON) used to receive the data needed to create a new project.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    name = project.name
    description = project.description
    if name :
        project_db = utils_db_project.read_project_by_project_name_user(name, auth_user)
        if not project_db:
            new_project = db.Project(name=name, description=description, owner=auth_user.user_id)
            utils_db_project.create_project(new_project)
            return {'message': f"Project '{name}' successfully created."}
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Project name '{name}' is currently used, changed it.")
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="Missing project name, please provide, at least, the name for the new project.")

@app.get("/project/{project_id}/info")
def get_project_details(project_id:int,
                        auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> models.ProjectOut:
    """
    Endpoint to retrieve the details of a specific project.
    :param project_id: id of the project to retrieve.
    :param auth_user: dependency injection with the process of authentication.
    :return: Project pydantic model with the information about the project.
    """
    if project_id:
        is_project_participant = utils_db_project.validate_project_participant(project_id, auth_user)
        if is_project_participant:
            project_db = utils_db_project.read_project_by_project_id(project_id)
            return models.ProjectOut(**project_db.to_dict())
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail='Invalid project id provided.')

@app.put("/project/{project_id}/info")
def update_project_details(project_id:int, project: models.ProjectIn,
                           auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to update the details of a specific project.
    :param project_id: id of the project (int) to update.
    :param project: Project model (JSON) used to receive the data used to update the project.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    name = project.name
    description = project.description
    is_project_participant = utils_db_project.validate_project_participant(project_id, auth_user)
    if is_project_participant:
        utils_db_project.update_project(project_id, name, description)
        return {'message': 'Project details updated successfully.'}
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

@app.delete("/project/{project_id}")
def delete_project(project_id:int,
                   auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to delete a specific project.
    :param project_id: id of the project (int) to delete.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    utils_db_project.delete_project(project_id, auth_user)
    return {'message': 'Project deleted successfully.'}

@app.get("/project/{project_id}/invite")
def grant_access_to_user(project_id:int, username:str,
                         auth_user: Annotated[db.User, Depends(Authenticator.authentication)]) -> dict[str, str]:
    """
    Endpoint to grant a user access to a specific project. This user is not the original project owner.
    :param project_id: id of the project (int) to grant access.
    :param username: name of the user (str) to grant access to.
    :param auth_user: dependency injection with the process of authentication.
    :return: dict (JSON) containing a message with the result of the operation.
    """
    project_db = utils_db_project.read_project_by_project_id(project_id)
    new_participant_db = utils_db_user.read_user_by_username(username)
    if project_db.owner == auth_user.user_id:
        utils_db_project.create_project_participation(project_id, new_participant_db, auth_user)
        return {'message': f"You've granted access to '{username}' to use this project."}
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)