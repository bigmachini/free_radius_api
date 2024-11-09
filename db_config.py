from fastapi import FastAPI, HTTPException
from psycopg2 import pool
import configparser

# Read database configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

DB_CONFIG = {
    "host": config.get('database', 'host'),
    "port": config.getint('database', 'port'),
    "database": config.get('database', 'database'),
    "user": config.get('database', 'user'),
    "password": config.get('database', 'password')
}
# Initialize connection pool
db_pool = pool.SimpleConnectionPool(1, 10, **DB_CONFIG)


# Helper function to get database connection from pool
def get_db_connection():
    try:
        conn = db_pool.getconn()
        if conn:
            return conn
        else:
            raise HTTPException(status_code=500, detail="Failed to get database connection")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection error") from e
