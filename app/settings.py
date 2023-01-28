# import os
import settings

DATABASE_SETTINGS = {
    'MAIN_DB_IS_SQLITE': True,
    'MAIN_DB_SQLALCHEMY_URL': 'sqlite:///./sql_app.sqlite',
    'TEST_DB_SQLALCHEMY_URL': 'sqlite:///./sql_test_app.sqlite',
}

if hasattr(settings, 'DB_SETTINGS'):
    for k, v in settings.DB_SETTINGS.items():
        if v is not None:
            DATABASE_SETTINGS[k] = v

