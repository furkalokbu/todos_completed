import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# environ.Env.read_env()
# env = environ.Env()

# SQLALCHEMY_DATABASE_URL = f"postgresql://{env('POSTGRES_USER')}:{env('POSTGRES_PASSWORD')}@{env('DB_IP')}/{env('POSTGRES_DB')}"
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessoinLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
