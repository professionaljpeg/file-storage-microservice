import MySQLdb
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.environ.get("FILESTOREDBHOST")
user = os.environ.get("FILESTOREDBUSER")
passwd = os.environ.get("FILESTOREDBPW")
db = os.environ.get("FILESTOREDB")

def connect_to_database(host = host, user = user, passwd = passwd, db = db):
    db_connection = MySQLdb.connect(host,user,passwd,db)
    return db_connection

def execute_query(db_connection = None, query = None, query_params = ()):

    if db_connection is None:
        print("No connection to the database found! Remember to call connect_to_database().")

    if query is None or len(query.strip()) == 0:
        print("Query is empty! Please pass an SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params))

    cursor = db_connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(query, query_params)
    db_connection.commit()
    return cursor
