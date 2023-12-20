from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from datetime import datetime


Base = declarative_base()

class RedditItemDB(Base):
    __tablename__ = 'reddit_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rank = Column(Integer, nullable=True, default=None)
    comments = Column(Integer, nullable=True, default=None)
    load_order = Column(Integer, nullable=True, default=10)
    url = Column(String, nullable=True, default=None)
    file_id = Column(String, nullable=True, default=None)
    signature = Column(String, nullable=True, default=None)
    posted_by = Column(String, nullable=True, default=None)
    posted_when = Column(Integer, nullable=True, default=None)
    date_added = Column(Date, nullable=True, default=datetime.today().date)
    checked = Column(Boolean, default=False, nullable=True)
    approved = Column(Boolean, default=False, nullable=True)
    published = Column(Boolean, default=False, nullable=True)
    my_comment = Column(String, default=None, nullable=True)

class Statistics(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    all_published_count = Column(Integer, default=0)
    all_deleted_count = Column(Integer, default=0)
    published_suggested_count = Column(Integer, default=0)
    published_manual_count = Column(Integer, default=0)
    max_rank_of_suggested = Column(Integer, default=0)
    min_rank_of_suggested = Column(Integer, default=100)
    mean_rank_of_suggested = Column(Float, default=0)



DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')  
DB_PORT = os.environ.get('DB_PORT')       
DB_NAME = os.environ.get('DB_NAME')

# Construct the PostgreSQL database URL
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create engine
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)


# Create a session
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Check if a row with id = 1 already exists
    existing_statistics = session.query(Statistics).filter_by(id=1).first()

    # If the row doesn't exist, create a new row
    if not existing_statistics:
        new_statistics = Statistics()
        session.add(new_statistics)
        session.commit()

except Exception as e:
    session.rollback()

finally:
    # Close the session
    session.close()
