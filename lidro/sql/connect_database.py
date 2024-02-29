""" Connect Database
"""
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker


def connect_to_database(db_name, user, password, host="localhost", port="5432"):
    """
    Connect Database PostgreSQL.

    Args:
        db_name (str): Name of database
        user (str): Name of user
        password (str): Password
        host (str): Hostname
        port (str): Port

    Returns:
        sqlalchemy.engine.Engine: Motor Database SQLAlchemy
        sqlalchemy.orm.Session: Session SQLAlchemy
    """
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(db_url)

    # Essayer de se connecter à la base de données
    try:
        engine.connect()
        print("database connection established successfully.")
    except exc.OperationalError:
        print("The database doesn't exist or the credentials are incorrect.")
        return None, None

    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session
