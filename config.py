import os
import psycopg2

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL
dbuser = 'postgres'
dbpass = 'postgres'
dbhost = 'localhost'
dbport = 5432 
dbname = 'fyyur'
SQLALCHEMY_DATABASE_URI = f'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}'
