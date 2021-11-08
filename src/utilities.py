import psycopg2
import os


def db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))
