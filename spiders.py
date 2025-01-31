import logging
import requests
from items import RedditItem
from pipelines import RedditPipeline
from selectolax.parser import HTMLParser
from traceback import print_exc
from time import sleep

class RedditscraperSpider:
    name = "redditScraper"
    allowed_domains = ["www.reddit.com"]
    target_url = "https://old.reddit.com/r/ProgrammerHumor/new/"
    TIMEOUT = 5  # Timeout value for HTTP requests (5 seconds)
    SCROLL_LIMIT = 2  # Set your desired scroll limit

    def __init__(self):
        self.items_pipeline = RedditPipeline()

    def extract_post_information(self, tree):
        posts = tree.css("div.thing")
        for post in posts:
            if post.attributes.get("data-promoted") == 'false':
                if post.css_first("span.linkflairlabel").text() == "Meme":
                    rank_element = post.attributes.get("data-score")
                    rank = rank_element if rank_element is not None else ''

                    comments_element = post.attributes.get("data-comments-count")
                    comments = comments_element if comments_element is not None else ''

                    url_element = post.css_first('a.thumbnail')
                    url = url_element.attributes.get('href', '') if url_element is not None else ''

                    signature_element = post.css_first("a.title")
                    signature = signature_element.text() if signature_element is not None else ''

                    posted_by_element = post.css_first('a.author')
                    posted_by = posted_by_element.text() if posted_by_element is not None else ''

                    posted_when_element = post.css_first('time')
                    posted_when = posted_when_element.text() if posted_when_element is not None else ''

                    item = RedditItem(rank, comments, url, signature, posted_by, posted_when)
                    self.items_pipeline.process_item(item)

    def go_to_next_page(self, html):
        tree = HTMLParser(html)
        next_button = tree.css_first('a[rel="nofollow next"]')
        if next_button:
            next_url = next_button.attributes.get('href')
            return next_url
        return None

    def run_spider(self):
        logging.info("Spider is starting...")
        logging.basicConfig(level=logging.INFO)
        try:
            current_url = self.target_url
            for _ in range(self.SCROLL_LIMIT):
                response = requests.get(
                    url='https://proxy.scrapeops.io/v1/',
                    params={
                        'api_key': 'your api key here',
                        'url': current_url
                    },
                )
                if response.status_code == 200:
                    html = response.content
                    tree = HTMLParser(html)
                    self.extract_post_information(tree)
                    next_url = self.go_to_next_page(html)
                    if next_url:
                        current_url = next_url
                        logging.info(f"Navigating to next page: {next_url}")
                        sleep(1)  # Adding a delay to avoid hitting the server too frequently
                    else:
                        logging.info("No next page found.")
                        break
                else:
                    logging.error(f"Failed to fetch URL: {current_url}. Status code: {response.status_code}")
                    break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print_exc()
        finally:
            logging.info("Spider finished.")
            self.items_pipeline.save_items_to_db()
