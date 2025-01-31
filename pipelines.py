import pandas as pd
from items import RedditItem
import re
from sqlalchemy.orm.exc import NoResultFound
from models import RedditItemDB, Session
from sqlalchemy import func
import logging
class RedditPipeline:

    new_items_count = 0  # Change the attribute name

    def __init__(self):
        self.items = []
        self.session = Session()

    @classmethod
    def increment_new_items_count(cls):
        cls.new_items_count += 1  # Change the attribute name

    @classmethod
    def get_new_items_count(cls):
        return cls.new_items_count  # Change the attribute name

    @classmethod
    def reset_new_items_count(cls):
        cls.new_items_count = 0  # Change the attribute name

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
        # Get the maximum and second-highest load orders
        max_load_order = self.session.query(func.max(RedditItemDB.load_order)).scalar()
        second_highest_load_order = self.session.query(func.max(RedditItemDB.load_order)).filter(RedditItemDB.load_order < max_load_order).scalar()

        # If there is no second highest load order, set a default value
        if second_highest_load_order is None:
            second_highest_load_order = 0

        # Calculate the new load order
        new_load_order = second_highest_load_order + 10

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
            self.increment_new_items_count() # Increment the count for new items

        # Add item to the list
        self.items.append(item)

    def save_items_to_db(self):
        logging.info("Saving to db.")

        try:
            # Commit changes to the database
            self.session.commit()
        except Exception as e:
            logging.error(f"An error occurred while saving items to the database: {e}")
        finally:
            # Close the session
            logging.info(f"Number of new items added to the database: {self.new_items_count}")
            self.session.close()

    def save_items_to_csv(self):
        if not self.items:
            logging.info("No items to save.")
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

        logging.info(f"Items saved to {csv_file_path}")
