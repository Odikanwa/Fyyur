import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASS')
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@localhost:5432/fyyurapp'.format(db_user, db_password)
SQLALCHEMY_TRACK_MODIFICATIONS = False


