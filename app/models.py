"""
Definición de la base de datos principal utilizada por la aplicación
"""
import datetime
from typing import Self

from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy import Column, ForeignKey, String, Integer, Date, DateTime, func, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from app import settings
from app.validators import validate_rut

SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_SETTINGS.get('MAIN_DB_SQLALCHEMY_URL'))

assert SQLALCHEMY_DATABASE_URL is not None

if settings.DATABASE_SETTINGS.get('MAIN_DB_IS_SQLITE'):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        future=True
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)


MainSessionDatabase = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def get_main_db():
    db = MainSessionDatabase()
    try:
        yield db
    finally:
        db.close()


MainBase = declarative_base()


def start_db():
    MainBase.metadata.create_all(bind=engine)


class ModelMixin:

    id = Column(Integer, primary_key=True)

    def save(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)

    @classmethod
    def delete(cls, db: Session, id: int):
        db.query(cls).filter(cls.id == id).delete()

    def update(self):
        pass

    @classmethod
    def get(cls, db: Session, id: int) -> Self:
        result: 'ModelMixin' = db.query(cls).get(id)
        return result

    @classmethod
    def get_all(cls, db: Session):
        return db.query(cls).all()


class Institution(ModelMixin, MainBase):
    __tablename__ = 'institution'

    name = Column(String(64))
    description = Column(String(128))
    address = Column(String(64))
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    projects = relationship('Project', back_populates='institution')

    @hybrid_property
    def google_address(self):
        parsed_address = str(self.address).strip().replace(' ', '%20')
        return 'https://www.google.com/maps/search/' + parsed_address
    
    @hybrid_property
    def abbreviated_name(self):
        return str(self.name)[:3].upper()
    



class Project(ModelMixin, MainBase):
    __tablename__ = 'project'
    name = Column(String(64))
    description = Column(String(128))
    start = Column(Date())
    end = Column(Date())

    institution_id = Column(Integer, ForeignKey('institution.id'))
    institution = relationship('Institution', back_populates='projects')
    manager_id = Column(Integer, ForeignKey('user.id'))

    manager = relationship('User', back_populates='projects')

    @hybrid_property
    def days(self) -> int:
        start = self.start if self.start > datetime.date.today() else datetime.date.today() 
        delta: datetime.timedelta = self.end - start  # type: ignore
        if delta.days < 0:
            return 0
        return delta.days


class User(ModelMixin, MainBase):
    __tablename__ = 'user'
    name = Column(String(64))
    last_name = Column(String(64))
    rut = Column(String(64))
    day_of_birth = Column(Date())
    role = Column(String(64))

    projects = relationship('Project', back_populates='manager')
    __table_args__ = (
        UniqueConstraint('rut', name='do_not_repeat_rut'),
    )

    @hybrid_property
    def age(self) -> int:
        current = datetime.date.today()
        birthday: datetime.date = self.day_of_birth  # type: ignore
        delta_year = current.year - birthday.year

        remove = 0
        if current.month < birthday.month:
            remove = 1
        elif current.month == birthday.month and current.day < birthday.day:
            remove = 1

        return delta_year - remove

    @classmethod
    def find_by_rut(cls, db: Session, rut: str) -> Self:
        result = db.query(cls).filter(
            cls.rut == rut).first()     # type: ignore
        return result

    def save(self, db: Session):
        validate_rut(str(self.rut))
        return super().save(db)
