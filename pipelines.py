import pandas as pd
from items import RedditItem
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from models import RedditItemDB, Session
from sqlalchemy import func

class RedditPipeline:
    def __init__(self):
        self.items = []
        self.session = Session()

    def extract_integer(self, value):
        # Extract all integers from the string, join them, and convert to integer
        numerical_part = ''.join(re.findall(r'\d+', value.strip()))
        return int(numerical_part) if numerical_part else 0

    def extract_time_in_days(self, value):
        # Extract all numerical parts using regex
        numerical_parts = re.findall(r'\d+', value.strip()) if value and value.strip() else []

        # If 'hour' is in the value, set the numerical part to 1
        return int(0) if 'day' not in value else int(numerical_parts[0]) if numerical_parts else 0

    def set_load_order(self):
        max_load_order = self.session.query(func.max(RedditItemDB.load_order)).scalar()
        new_load_order = (max_load_order + 10) if max_load_order is not None else 10
        return new_load_order

    def process_item(self, item):
        # Handle modifications for 'rank', 'comments', and 'posted_when'
        item.rank = self.extract_integer(item.rank)
        item.comments = self.extract_integer(item.comments)
        item.posted_when = self.extract_time_in_days(item.posted_when)

        try:
            # Check if an item with the same 'posted_by' and 'signature' exists
            db_item = self.session.query(RedditItemDB).filter_by(
                posted_by=item.posted_by, signature=item.signature
            ).one()

            # Update existing item
            db_item.rank = item.rank
            db_item.comments = item.comments
            db_item.posted_when = item.posted_when

        except NoResultFound:
            # Create a new item if it doesn't exist
            db_item = RedditItemDB(
                rank=item.rank,
                comments=item.comments,
                load_order=self.set_load_order(),
                url=item.url,
                signature=item.signature,
                posted_by=item.posted_by,
                posted_when=item.posted_when,
            )
            self.session.add(db_item)

        # Add item to the list
        self.items.append(item)

    def save_items_to_db(self):
        try:
            # Commit changes to the database
            self.session.commit()
            print("Items saved to the database.")
        except Exception as e:
            print(f"An error occurred while saving items to the database: {e}")
        finally:
            # Close the session
            self.session.close()



    def save_items_to_csv(self):
        if not self.items:
            print("No items to save.")
            return

        # Convert items list to a list of dictionaries
        items_dict_list = []
        for item in self.items:
            items_dict_list.append({
                'Rank': item.rank,
                'Comments': item.comments,
                'URL': item.url,
                'Signature': item.signature,
                'Posted By': item.posted_by,
                'Posted When': item.posted_when
            })

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(items_dict_list)

        csv_file_path = 'reddit_items.csv'
        df.to_csv(csv_file_path, index=False, encoding='utf-8')

        print(f"Items saved to {csv_file_path}")

