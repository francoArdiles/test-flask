from typing import List
from datetime import date

from pydantic import BaseModel


class BaseInstitution(BaseModel):
    name: str
    description: str
    address: str


class CreateInstitution(BaseInstitution):
    pass


class Institution(BaseInstitution):
    id: int
    created_at: date

    class Config:
        orm_mode = True


class GoogleInstitution(Institution):
    google_address: str
    abbreviated_name: str


class InstitutionList(BaseModel):
    institutions: List[Institution]


class InstitutionGoogleList(BaseModel):
    institutions: List[GoogleInstitution]


class BaseUser(BaseModel):
    name: str
    last_name: str
    rut: str
    day_of_birth: date
    role: str


class CreateUser(BaseUser):
    pass


class User(BaseUser):
    age: int
    id: int

    class Config:
        orm_mode = True


class UserList(BaseModel):
    users: List[User]


class BaseProject(BaseModel):
    name: str
    description: str
    start: date
    end: date
    institution_id: int
    manager_id: int


class CreateProject(BaseProject):
    pass


class Project(BaseProject):
    id: int

    class Config:
        orm_mode = True


class ProjectList(BaseModel):
    projects: List[Project]


class ProjectAndResponsible(BaseModel):
    name: str
    description: str
    start: date
    end: date
    manager: User

    class Config:
        orm_mode = True


class ProjectEstimatedTime(BaseModel):
    id: int
    name: str
    days: int

    class Config:
        orm_mode = True


class ProjectListTimes(BaseModel):
    projects: List[ProjectEstimatedTime]


class InstitutionProjects(Institution):
    projects: List[ProjectAndResponsible]


class UserProjects(User):
    projects: List['Project']
