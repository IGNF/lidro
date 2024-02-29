# import pytest

from lidro.sql.connect_database import connect_to_database

# from lidro.sql.create_database import create_geospatial_database

db_name = "test_hydro"  # database name for creating
db_user = "mudpays"  # username for PostgreSQL
db_password = ""  # Password for PostgreSQL authentification


def test_connect_database():
    engine, session = connect_to_database(db_name, db_user, db_password, "localhost", "5432")

    # assert engine is not None

    # if engine is not None:
    #     create_geospatial_database(engine, db_name)
