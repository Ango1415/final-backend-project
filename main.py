from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel

from example_data import users, projects

user_logged = None

class User(BaseModel):
    name: str
    password: str
    check_password: Union[str, None] = None

class Project(BaseModel):
    id: str
    name: str
    description: str = None
    owner: str = None
app = FastAPI()


@app.get("/auth")
def get_users():
    return users

# Project requirements
@app.post("/auth")
def create_user(user: User):
    """
    Allows the creation of users into the system
    :param user: Account username and password (JSON)
    :return: dict with a message related to the process done
    """
    global users

    name = user.name
    password = user.password
    check_password = user.check_password

    if name and password and check_password:    #Checks if the user provides the entire info needed for the process
        existing_user = name in [user['name'] for user in users] # Checks if the user already exists
        if existing_user:
            return {
                'message': f"Username '{name}' is not unavailable, try using another one"
            }
        else:
            if password != check_password: #Checks if the user writes correctly his password
                return {'message': f"Your password and its repetition are not the same, try it again please."}
            else:
                # Successfully register the new account
                new_user = {'name': name, 'password': password}
                users.append(new_user)
                return {'message': f"User '{name}' successfully created!"}
    else:
        return {
            'message': "You must to provide proper username and password to sign up, please fill in the entire form"
        }

@app.post("/login")
def login_service(user: User):
    usernames = [user['name'] for user in users]
    if user.name in usernames:
        index = usernames.index(user.name)
        if users[index]['password'] == user.password:
            global user_logged
            user_logged = user.name
            return {'message': "Logged in successfully!", 'current_user': user_logged}
        else:
            return {'message': "Incorrect username and/or password."}
    return {'message': "Incorrect username and / or password."}

@app.get("/logout")
def logout_service():
    global user_logged
    if user_logged:
        user_logged = None
        return {'message': "Successfully logged out!", 'current_user': user_logged}
    else:
        return {'message': "No Session is active right now!"}

@app.get("/projects")
def get_projects():
    if user_logged:
        user_projects: List[dict] = [project for project in projects if user_logged in project['owner']]
        if len(user_projects) == 0:
            return {'message': "No projects created yet!"}
        else:
            return user_projects
    else:
        return {'message': 'You must to be logged in, try it first.', 'current_user': user_logged}

@app.post("/projects")
def create_project(project: Project):
    if user_logged:
        id = project.id
        name = project.name
        if id and name:
            user_project_ids = [project['id'] for project in projects if user_logged in project['owner']]
            if id in user_project_ids:
                return  {'message': f"Id '{id}' is currently used, changed it.", 'current_user': user_logged}
            else:
                project = project.model_dump()
                project['owner'] = user_logged
                projects.append(project)
                return {'message':f"Project '{project['name']}' successfully created.", 'project_id': project['id'], 'current_user': user_logged}
        else:
            return {
            'message': "Missing data, please fill in the entire form to create a new project."
        }
    else:
        return {'message': 'You must be logged in, try it first.', 'current_user': user_logged}

@app.get("/project/{project_id}/info")
def get_project_details(project_id:str):
    if user_logged:
        user_projects = [project for project in projects if user_logged in project['owner']]
        user_projects_ids = [project['id'] for project in user_projects]
        if project_id in user_projects_ids:
            index = user_projects_ids.index(project_id)
            return  user_projects[index]
        else:
            return {'message': 'No projects were found with that id. Try it again.', 'current_user': user_logged}
    else:
        return {'message': 'You must to be logged in, try it first.', 'current_user': user_logged}

@app.put("/project/{project_id}/info")
def update_project_details(project_id:str, project: Project):
    if user_logged:
        user_projects = [project for project in projects if user_logged in project['owner']]
        user_projects_ids = [project['id'] for project in user_projects]
        if project_id in user_projects_ids:
            index = user_projects_ids.index(project_id)
            user_projects[index].update(project.model_dump())
            user_projects[index]['owner'] = user_logged
            return {'message': 'Project successfully updated!', 'project_info': user_projects[index], 'current_user': user_logged}
        else:
            return {'message': 'No projects were found with that id. Try it again.', 'current_user': user_logged}
    else:
        return {'message': 'You must to be logged in, try it first.', 'current_user': user_logged}

@app.delete("/project/{project_id}")
def delete_project(project_id:str):
    if user_logged:
        user_projects = [project for project in projects if user_logged in project['owner']]
        user_projects_ids = [project['id'] for project in user_projects]
        if project_id in user_projects_ids:
            for index, project in enumerate(projects):
                if project['id'] == project_id and user_logged in project['owner'] :
                    project_deleted = projects.pop(index)
                    return {'message': 'Project successfully deleted!', 'project_info': project_deleted, 'current_user': user_logged}
            return {'message': 'Project unsuccessfully deleted, try it again please', 'current_user': user_logged}
        else:
            return {'message': 'No projects were found with that id. Try it again.', 'current_user': user_logged}
    else:
        return {'message': 'You must to be logged in, try it first.', 'current_user': user_logged}

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