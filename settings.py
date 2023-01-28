"""
Archivo encargado de obtener las variables de entorno como constantes en la 
aplicación.
"""

import os

from dotenv import load_dotenv  # type: ignore

load_dotenv()


DB_SETTINGS = {
    'MAIN_DB_IS_SQLITE': os.getenv("MAIN_DB_IS_SQLITE", 'TRUE').upper() == 'TRUE',

    'MAIN_DB_SQLALCHEMY_URL': os.getenv("MAIN_DB_SQLALCHEMY_URL", None),

    'TEST_DB_SQLALCHEMY_URL': os.getenv('TEST_DB_SQLALCHEMY_URL', None),
}
