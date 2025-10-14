from fastapi import FastAPI
from data import users, projects

app = FastAPI()


@app.get("/")
async def root():
    """
    First endpoint for testing
    :return: dict with a message related to the process done
    """
    return {"message": "Hello World"}

# Project requirements
@app.post("/auth")
def create_user(user:str, password:str, check_password:str):
    """
    Allows the creation of users into the system
    :param user: Account username
    :param password: Account password
    :param check_password:  Checks if the password was correctly written
    :return: dict with a message related to the process done
    """
    if user and password and check_password:    #Checks if the user provides the entire info needed for the process
        existing_user = users.get(user, None) # Checks if the user already exists
        if existing_user:
            return {
                'message': f"Username '{user}' is not currently available, try using another one"
            }
        else:
            if password != check_password: #Checks if the user writes correctly his password
                return {'message': f"Your password and its repetition are not the same, try it again please."}
            else:
                # Successfully register the new account
                users[user] = password
                return {'message': f"User '{user}' successfully created!"}
    else:
        return {
            'message': "You have to provide proper username and password to sign up, please fill in the whole form"
        }




# Endpoints to develop
"""@app.post("/login")
def login_service(user:str, password:str):
    return {'message': "You're in the login service"}

@app.post("/projects")
def create_project(project_name:str, description:str):
    return {'message': "You're in the get_projects service"}

@app.get("/projects")
def get_projects():
    return {'message': "You're in the get_projects service"}

@app.get("/project/<project_id>/info")
def get_project_details(project_id:int):
    return {'message': "You're in the get_project_details service"}

@app.put("/project/<project_id>/info")
def update_project_details(project_id:int, project_name:str, description:str):
    return {'message': "You're in the update_project_details service"}

@app.delete("/project/<project_id>")
def delete_project(project_id:int):
    return {'message': "You're in the delete_project service"}

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