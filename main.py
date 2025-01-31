import logging
import schedule
import pytz
import time
import telebot
from datetime import datetime

from items import RedditItem
from pipelines import RedditPipeline
from spiders import RedditscraperSpider

# Initialize the Telegram bot
bot_token = '6839500085:AAHjFcHrBiNNTuR3m8-2sWH-2i3q9_HkUjE'
bot = telebot.TeleBot(bot_token, parse_mode='HTML')

# Get the target channel information
chat_id = '-1001999613821'

pipeline = RedditPipeline()
spider = RedditscraperSpider()


def get_items_added_to_db_count():
    try:
        new_items_count = RedditPipeline.get_new_items_count()
        logging.info(f"Number of new items saved to the database: {new_items_count}")
        return new_items_count

    except Exception as e:
        logging.error(f"An error occurred in the main script: {e}")
        return None

def convert_to_local_time(moscow_hour, moscow_minute):
    try:
        # Define the Moscow timezone
        moscow_tz = pytz.timezone('Europe/Moscow')

        # Get the current time in Moscow
        moscow_time = datetime.now(moscow_tz).replace(hour=moscow_hour, minute=moscow_minute, second=0, microsecond=0)

        # Convert Moscow time to local time
        local_tz = pytz.timezone('Europe/Berlin')
        local_time = moscow_time.astimezone(local_tz)

        # Format the local time as a string in %H:%M format
        formatted_time = local_time.strftime('%H:%M')

        return formatted_time

    except Exception as e:
        logging.error(f"Error converting to local time: {e}")
        return None

# Define constants for time intervals
NIGHT_TIME = [
    convert_to_local_time(4, 0)
]

DAY_TIME = [
    convert_to_local_time(16, 0)
]

def send_message_to_bot(message):
    try:
        bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error(f"Error sending message to bot: {e}")

def schedule_scrapping():
    # Schedule posting for morning andevening times
    for time_interval in DAY_TIME:
        schedule.every().day.at(time_interval).do(run_spider_and_send_message, 'the afternoon', message=None).tag('morning')

    for time_interval in NIGHT_TIME:
        schedule.every().day.at(time_interval).do(run_spider_and_send_message, 'night', message=None).tag('evening')

    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to avoid high CPU usage

def run_spider_and_send_message(time_of_day, message=None):
    try:
        spider.run_spider()
        new_items_count = get_items_added_to_db_count()
        if new_items_count is not None:
            response_message = f"Scraping and processing completed successfully at {time_of_day}. {new_items_count} new items were added to the database."
        elif new_items_count == 0:
            response_message = f"Scraping and processing completed with an error at {time_of_day}. Check the logs for details."
        else:
            response_message = f"Scraping and processing completed with an error at {time_of_day}. Check the logs for details."

        send_message_to_bot(response_message)

        # Reset the count after sending the message
        RedditPipeline.reset_new_items_count()

    except Exception as e:
        logging.error(f"An error occurred during scraping and processing: {e}")
        error_message = f"An error occurred during scraping and processing at {time_of_day}. Check the logs for details."
        send_message_to_bot(error_message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Running Main")
    bot.send_message(chat_id, "Бот запущен, ожидайте сообщения о статусе операций.")
    run_spider_and_send_message(datetime.now())
    schedule_scrapping()
