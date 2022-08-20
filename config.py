from importlib.machinery import DEBUG_BYTECODE_SUFFIXES
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
class MyLocal:
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1111abc@localhost:5432/fyyur'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
