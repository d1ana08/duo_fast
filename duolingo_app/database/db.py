from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'postgresql://postgres:admin@localhost/fast_duolingo_db'
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()