from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from hashlib import sha1
from jwt.exceptions import InvalidTokenError
import jwt
import uvicorn

import models
import database.db_orm as db
import utils_db


# Setting for the JWT encoding.
SECRET_KEY = '-SuP3R_s3Cr3T_K3Y*'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 10

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

app = FastAPI()


def authentication(token: Annotated[str, Depends(oauth2_scheme)]) -> db.User:
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get('sub')
            auth_user = utils_db.read_user_by_username(username)
            if auth_user:
                return auth_user
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access (the provided username doesn't match with our system), login again.",
                headers={'WWW-Authenticate': 'Bearer'})
        except InvalidTokenError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access You must provide a valid token, login again.",
                headers={'WWW-Authenticate': 'Bearer'})
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                detail="No current platform access. You must provide a valid token, login again.",
                headers={'WWW-Authenticate': 'Bearer'})


# Project requirements
@app.post("/auth")
def create_user(user: models.UserIn) -> dict:
    username = user.username
    password = user.password
    check_password = user.check_password
    if username and password and check_password:
        username_db = utils_db.read_user_by_username(username)
        if not username_db:
            if password == check_password:
                new_user = db.User(username=username, password=sha1(password.encode()).hexdigest())
                utils_db.create_user(new_user)
                return {'message': f"User '{user.username}' successfully created!"}
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"Your password and its repetition don't match, try it again please.")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Username '{username}' already in use, try using another one")
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail="You must to provide proper username and password to sign up, please fill in the entire form")

@app.post("/login")
def login_service(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.Token:
    username = form_data.username
    password = sha1(form_data.password.encode()).hexdigest()
    if username and password:
        user_db = utils_db.read_user_by_username_password(username, password)
        if user_db:
            if ACCESS_TOKEN_EXPIRE_MINUTES:
                expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            else:
                expire = timedelta(minutes=5)
            expire += datetime.now(timezone.utc)
            data = {'sub': user_db.username, 'exp': expire}
            access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
            return models.Token(access_token=access_token, token_type='bearer')

        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect username and / or password.",
                            headers={'WWW-Authenticate': 'Bearer'})
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="Missing data, please fill in the entire form.")

@app.get("/projects")
def get_projects(auth_user: Annotated[db.User, Depends(authentication)]) -> Union[list[models.ProjectOut], dict]:
    projects_db = utils_db.read_participant_projects(auth_user)
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
                   auth_user: Annotated[db.User, Depends(authentication)]) -> dict:
    name = project.name
    description = project.description
    if name :
        project_db = utils_db.read_project_by_project_name_user(name, auth_user)
        if not project_db:
            new_project = db.Project(name=name, description=description, owner=auth_user.user_id)
            utils_db.create_project(new_project)
            return {'message': f"Project '{name}' successfully created."}
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Project name '{name}' is currently used, changed it.")
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail="Missing project name, please provide, at least, the name for the new project.")

@app.get("/project/{project_id}/info")
def get_project_details(project_id:int,
                        auth_user: Annotated[db.User, Depends(authentication)]) -> models.ProjectOut:
    if project_id:
        is_project_participant = utils_db.validate_project_participant(project_id, auth_user)
        if is_project_participant:
            project_db = utils_db.read_project_by_project_id(project_id)
            return models.ProjectOut(**project_db.to_dict())
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                        detail='Invalid project id provided.')

@app.put("/project/{project_id}/info")
def update_project_details(project_id:int, project: models.ProjectIn,
                           auth_user: Annotated[db.User, Depends(authentication)]) -> dict[str, str]:
    name = project.name
    description = project.description
    is_project_participant = utils_db.validate_project_participant(project_id, auth_user)
    if is_project_participant:
        utils_db.update_project(project_id, name, description)
        return {'message': 'Project details updated successfully.'}
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

@app.delete("/project/{project_id}")
def delete_project(project_id:int,
                   auth_user: Annotated[db.User, Depends(authentication)]) -> dict[str, str]:
    utils_db.delete_project(project_id, auth_user)
    return {'message': 'Project deleted successfully.'}




@app.post("/project/{project_id}/documents")
def upload_project_documents(project_id:int, documents:list[UploadFile],
                             auth_user: Annotated[db.User, Depends(authentication)]) -> dict[str, str]:
    if len(documents) != 0:
        is_project_participant = utils_db.validate_project_participant(project_id, auth_user)
        if is_project_participant:
            for document in documents:
                name = document.filename.lower().replace(' ', '_')
                file_format = document.content_type
                file_url = f'http://localhost:8000/project/{project_id}/documents/{name}'
                attached_project = project_id
                utils_db.create_document(
                    db.Document(name=name, format=file_format, file_url=file_url,attached_project=attached_project)
                )
            return {'message': f"{len(documents)} documents successfully uploaded."}
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="No documents were received to upload.")


@app.get("/project/{project_id}/documents")
def get_project_documents(project_id:int,
                          auth_user: Annotated[db.User, Depends(authentication)]) -> Union[list[models.DocumentOut], dict]:
    is_project_participant = utils_db.validate_project_participant(project_id, auth_user)
    if is_project_participant:
        documents_db = utils_db.read_documents(project_id)
        documents = []
        for document_db in documents_db:
            documents.append(models.DocumentOut(**document_db.to_dict()))
        if len(documents) > 0:
            return documents
        return {'message': f"This project doesn't have documents attached to it."}
    raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

@app.get("/document/{document_id}")
def download_project_document(document_id:int,
                              auth_user: Annotated[db.User, Depends(authentication)]):
    document_db = utils_db.read_document_by_id(document_id)
    if document_db:
        is_project_participant = utils_db.validate_project_participant(document_db.attached_project, auth_user)
        if is_project_participant:
            return models.DocumentOut(**document_db.to_dict())
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                        detail='No document was found with that id. Try it again.')


@app.put("/document/{document_id}")
def update_document(document_id:int, document:models.DocumentIn,
                    auth_user: Annotated[db.User, Depends(authentication)]):
    name = document.name
    url = document.file_url
    document_db = utils_db.read_document_by_id(document_id)
    if document_db:
        is_project_participant = utils_db.validate_project_participant(document_db.attached_project, auth_user)
        if is_project_participant:
            utils_db.update_document(document_id, name, url)
            return {'message': f"{name} document updated successfully."}
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                        detail='No document was found with that id. Try it again.')


@app.delete("/document/{document_id}")
def delete_project_document(document_id:int,
                            auth_user: Annotated[db.User, Depends(authentication)]):
    document_db = utils_db.read_document_by_id(document_id)
    if document_db:
        utils_db.delete_document(document_id, auth_user)
        return {'message': f"Document deleted successfully."}
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                        detail='No document was found with that id. Try it again.')


# Endpoints to develop
"""
@app.post("/project/<project_id>/invite?user=<login>")
def delete_project_document(project_id:int, login:str|None):
    return {'message': "You're in the delete_project_document service"}"""




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)