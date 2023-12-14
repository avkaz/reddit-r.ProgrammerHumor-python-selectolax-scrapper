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

    id = Column(Integer, primary_key=True)
    rank = Column(Integer)
    comments = Column(Integer)
    load_order = Column(Integer, default=10)
    url = Column(String)
    file_id = Column(Integer, default=None)
    signature = Column(String)
    posted_by = Column(String)
    posted_when = Column(Integer)
    date_added = Column(Date, default=datetime.today().date)
    checked = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    published = Column(Boolean, default=False)
    my_comment = Column(String, default=None)

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


DB_USER = 'avkaz'
DB_PASSWORD = 'avkazz_pass'
DB_HOST = 'localhost'  
DB_PORT = '5432'       
DB_NAME = 'reddit_items.db'

# Construct the PostgreSQL database URL
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create engine
engine = create_engine(db_url)
Base.metadata.create_all(bind=engine)


# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create a new row in the 'statistics' table with default values
new_statistics = Statistics()

# Add the new row to the session
session.add(new_statistics)

# Commit the session to persist the changes to the database
session.commit()

# Close the session
session.close()
