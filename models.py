from typing import Union
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class UserIn(BaseModel):
    username: str =  Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=100)
    check_password:str = Field(min_length=1, max_length=100)

# class UserOut(BaseModel):
#     user_id: int
#     username: str
#     password: str

class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: Union[str, None] = Field(min_length=0, max_length=200)

class ProjectOut(BaseModel):
    project_id: int
    name: str
    description: Union[str, None]
    owner: int

class DocumentIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    file_url: str = Field(min_length=1, max_length=200)

class DocumentOut(BaseModel):
    document_id: int
    name: str
    format: str
    file_url: str
    attached_project: int

