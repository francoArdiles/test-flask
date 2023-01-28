from app import models, schemas
from sqlalchemy.orm import Session


def get_projects(db: Session):
    return models.Project.get_all(db)


def get_users(db: Session):
    return models.User.get_all(db)


def get_institutions(db: Session):
    return models.Institution.get_all(db)


def get_institution(db: Session, id: int):
    return models.Institution.get(db, id)


def get_institution_projects(db: Session, id: int):
    institution = models.Institution.get(db, id)
    return institution


def get_user_by_rut(db: Session, rut: str):
    return models.User.find_by_rut(db, rut)


def create_institution(db: Session, data: schemas.CreateInstitution):
    institution = models.Institution(**data.dict())
    institution.save(db)
    return institution


def create_user(db: Session, data: schemas.CreateUser):
    user = models.User(**data.dict())
    user.save(db)
    return user


def create_project(db: Session, data: schemas.CreateProject):
    project = models.Project(**data.dict())
    project.save(db)
    return project
