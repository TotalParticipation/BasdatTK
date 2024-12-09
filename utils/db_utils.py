# import psycopg2
# import os

# def get_db_connection():
#     # Get database credentials from environment variables
#     db_name = os.environ.get("DB_NAME")
#     db_user = os.environ.get("DB_USER")
#     db_password = os.environ.get("DB_PASSWORD")
#     db_host = os.environ.get("DB_HOST")
#     db_port = os.environ.get("DB_PORT")

#     # Establish a connection to the database
#     connection = psycopg2.connect(
#         dbname=db_name,
#         user=db_user,
#         password=db_password,
#         host=db_host,
#         port=db_port
#     )

#     return connection
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    # Use the connection string directly
    tmpPostgres = "postgresql://TKBASDATDATABASE_owner:4aZLyG5uofbv@ep-curly-king-a1q2gfq8.ap-southeast-1.aws.neon.tech/TKBASDATDATABASE?sslmode=require"
    
    # Parse the connection string
    parsed_url = urlparse(tmpPostgres)
    
    # Extract components from the URL
    db_name = parsed_url.path[1:]  # Remove the leading '/' from the path
    db_user = parsed_url.username
    db_password = parsed_url.password
    db_host = parsed_url.hostname
    db_port = parsed_url.port

    # Establish a connection to the Neon database
    connection = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        sslmode="require"  # Required for Neon
    )

    return connection