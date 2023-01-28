from typing import Any

from pydantic.error_wrappers import ValidationError
from sqlalchemy.exc import IntegrityError
from flask import Flask, request

from app import controller, schemas
from app.models import MainSessionDatabase, start_db

start_db()

app = Flask(__name__)


@app.route("/")
def hello_world():
    """
    Ruta base con hello world

    Returns
    -------
    dict[str, str]
        Saludo de bienvenida
    """
    return {"greetings": "Hello, World!"}


@app.route('/institutions', methods=('GET', 'POST', ))
def institutions():
    """
    Endpoint encargado de mostrar y crear instituciones. Cuando recibe una
    request con método get, obtiene la lista de todas las instituciones
    registradas en la base de datos.
    Cuando recibe un método post, intenta crear una nueva institución con la
    información incluida en el body de la request con contenido tipo json.
    Esta información debe contener los campos name, description y address.

    Returns
    -------
    Lista con la información de las instituciones en caso de recibir una request
    GET, y en caso de recibir un POST, retorna la nueva institución creada
    """

    with MainSessionDatabase() as db:
        if request.method == 'GET':
            query_result = controller.get_institutions(db)
            if not query_result:
                return query_result
            institutions = schemas.InstitutionList.parse_obj(
                {"institutions": query_result})
            return institutions.dict()["institutions"]

        elif request.method == 'POST':
            assert isinstance(request.json, dict)
            body: dict[str, Any] = request.json
            try:
                institution = schemas.CreateInstitution(**body)
            except ValidationError as err:
                return err, 422
            db_institution = controller.create_institution(db, institution)
            return schemas.Institution.from_orm(db_institution).dict()



@app.route('/projects', methods=('GET', 'POST', ))
def projects():
    """
    Endpoint encargado de mostrar y crear proyectos. Cuando recibe una
    request con método get, obtiene la lista de todos los proyectos
    registradas en la base de datos.
    Cuando recibe un método post, intenta crear un nuevo proyecto con la
    información incluida en el body de la request con contenido tipo json.
    Esta información debe contener los campos name, description, institution_id,
    manager_id, start, end.

    Returns
    -------
    Lista con la información de los proyectos en caso de recibir una request
    GET, y en caso de recibir un POST, retorna el nuevo proyecto registrado
    """
    with MainSessionDatabase() as db:
        if request.method == 'GET':
            query_result = controller.get_projects(db)
            if not query_result:
                return query_result
            projects = schemas.ProjectList.parse_obj(
                {"projects": query_result})
            return projects.dict()["projects"]

        elif request.method == 'POST':
            assert isinstance(request.json, dict)
            body: dict[str, Any] = request.json
            try:
                project = schemas.CreateProject(**body)
            except ValidationError as err:
                return err, 422
            db_project = controller.create_project(db, project)
            return schemas.Project.from_orm(db_project).dict()


@app.route('/users', methods=('GET', 'POST', ))
def users():
    """
    Endpoint encargado de mostrar y crear usuarios. Cuando recibe una
    request con método get, obtiene la lista de todos los usuarios
    registradas en la base de datos.
    Cuando recibe un método post, intenta crear un nuevo usuario con la
    información incluida en el body de la request con contenido tipo json.
    Esta información debe contener los campos name, last_name, rut, 
    day_of_birth y role

    Returns
    -------
    Lista con la información de los usuarios en caso de recibir una request
    GET, y en caso de recibir un POST, retorna el nuevo usuario registrado
    """
    with MainSessionDatabase() as db:
        if request.method == 'GET':
            query_result = controller.get_users(db)
            if not query_result:
                return query_result
            users = schemas.UserList.parse_obj(
                {"users": query_result})
            return users.dict()["users"]

        elif request.method == 'POST':
            assert isinstance(request.json, dict)
            body: dict[str, Any] = request.json
            try:
                user = schemas.CreateUser(**body)
                db_user = controller.create_user(db, user)
            except IntegrityError:
                return 'El usuario no ha podido ser almacenado', 400
            except ValidationError as err:
                return err, 422
            except ValueError:
                return 'Se ha ingresado información errónea', 400
            return schemas.User.from_orm(db_user).dict()


@app.route('/institutions/<id>')
def institution(id: int):
    """
    Obtiene una única institución con su información base

    Parameters
    ----------
    id : int
        identificador de la institución

    Returns
    -------
    Diccionario con la información de la institución
    """
    # Levantar error
    with MainSessionDatabase() as db:
        if request.method == 'GET':
            query_result = controller.get_institution(db, id)
            if not query_result:
                # 404
                return 'No encontrado', 404
            institution = schemas.Institution.from_orm(query_result)
            return institution.dict()


@app.route('/institutions/<id>/projects', methods=['GET'])
def institution_projects(id: int):
    """
    Endpoint encargado de mostrar los proyectos de la institución con la
    información de la persona a cargo de dicho proyecto

    Parameters
    ----------
    id : int
        identificador de la institución

    """
    # Levantar error

    with MainSessionDatabase() as db:
        query_result = controller.get_institution(db, id)
        if not query_result:
            # 404
            return 'no encontrado', 404
        institution = schemas.InstitutionProjects.from_orm(query_result)
        institution.update_forward_refs()
        return institution.dict()


@app.route('/users/<rut>/projects', methods=['GET'])
def user(rut: str):
    """
    Obtiene un usuario y busca todos los proyectos asociados a este

    Parameters
    ----------
    rut : str
        rut del usuario

    Returns
    -------
    Entrega la información del usuario y todos los proyectos asociados a este
    """
    # Levantar error
    with MainSessionDatabase() as db:
        query_result = controller.get_user_by_rut(db, rut)
        if query_result is None:
            return 'No encontrado', 404
        user = schemas.UserProjects.from_orm(query_result)
        return user.dict()


@app.route('/institutions/maps', methods=['GET'])
def maps():
    """
    Endpoint que entrega la lista de todas las instituciones registradas en la
    base de datos presentando su dirección en el formato de url de google maps
    """
    with MainSessionDatabase() as db:
        query_result = controller.get_institutions(db)
        if not query_result:
            return query_result
        institutions = schemas.InstitutionGoogleList.parse_obj(
            {"institutions": query_result})
        return institutions.dict()["institutions"]


@app.route('/projects/estimations', methods=['GET'])
def projects_estimation():
    """
    Endpoint encargado de obtener una lista con todos los proyectos y el tiempo
    restante para su finalización
    """
    with MainSessionDatabase() as db:
        query_result = controller.get_projects(db)
        if not query_result:
            return query_result
        projects = schemas.ProjectListTimes.parse_obj(
            {"projects": query_result})
        return projects.dict()["projects"]


if __name__ == '__main__':
    app.run(debug=True)
