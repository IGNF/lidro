""" Create geospatial Database
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def create_geospatial_database(engine, db_name):
    """
    Creates a PostgreSQL geospatial database with the required schemas and extensions.

    Args:
        engine (sqlalchemy.engine.Engine): SQLAlchemy database engine
        db_name (str): Name of the database to create.
    """
    # Installer les extensions PostGIS
    with engine.connect() as conn:
        conn.execute("CREATE DATABASE IF NOT EXISTS %s;" % db_name)
        conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        conn.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")

    # Créer les schémas
    Base.metadata.create_all(engine)

    print("La base de données géospatiale a été créée avec succès.")
