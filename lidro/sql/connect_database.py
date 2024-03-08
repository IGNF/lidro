""" Connect Database
"""
from sqlalchemy import create_engine


def get_connection(db_name: str, user: str, password: str, host: str, port: int):
    """
    Connect Database PostgreSQL.

    Args:
        db_name (str): Name of database
        user (str): Name of user
        password (str): Password
        host (str): Hostname
        port (int): Port

    Returns:
        sqlalchemy.engine.Engine: Motor Database SQLAlchemy)
    """
    engine = create_engine(url="postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, db_name))
    return engine.connect()


def connect_to_database(db_name: str, user: str, password: str, host: str, port: int):
    """
    Connect Database PostgreSQL.

    Args:
        db_name (str): Name of database
        user (str): Name of user
        password (str): Password
        host (str): Hostname
        port (int): Port

    Returns:
        sqlalchemy.orm.Session: Session SQLAlchemy
    """
    try:
        # Get the connection objet (engine) for the database
        get_connection(db_name, user, password, host, port)
        print(f"Connection to the {host} for user {user} created successfully.")
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)
