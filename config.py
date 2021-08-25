# config.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

MYSQL_USER = 'projectmanager'

mysql_db_username = 'projectmanager'
mysql_db_password = 'project_manager'
mysql_db_name = 'user_dev'
mysql_db_hostname = 'localhost:3306'


class Config:
    SECRET_KEY = "jSMmpFXVyAfHjqOpyPirvA"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://cloudacademy:pfm_2020@host.docker.internal:3306/user_dev'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(
        DB_USER=mysql_db_username,
        DB_PASS=mysql_db_password,
        DB_ADDR=mysql_db_hostname,
        DB_NAME=mysql_db_name)
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):

    ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://projectmanager:project_manager@project-database:3306/project-db-prod'
