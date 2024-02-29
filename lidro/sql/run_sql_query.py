""" Run a SQL query against the database
"""
from sqlalchemy import exc


def execute_sql_query(session, query):
    """
    Runs a SQL query against the database

    Args:
        session (sqlalchemy.orm.Session): Session SQLAlchemy
        query (str): SQL query to execute

    Returns:
        list: Résultats de la requête.
    """
    try:
        result = session.execute(query)
        return result.fetchall()
    except exc.SQLAlchemyError as e:
        print("Error executing query:", e)
        return None


# if __name__ == "__main__":
#     db_name = input("Entrez le nom de la base de données PostgreSQL : ")
#     db_user = input("Entrez votre nom d'utilisateur PostgreSQL : ")
#     db_password = input("Entrez votre mot de passe PostgreSQL : ")

#     engine, session = connect_to_database(db_name, db_user, db_password)

#     if engine is not None:
#         create_geospatial_database(engine, db_name)
#         session.close()
