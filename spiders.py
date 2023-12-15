# reddit_spider.py
import logging
from playwright.sync_api import sync_playwright
from items import RedditItem
from pipelines import RedditPipeline
from selectolax.parser import HTMLParser
from traceback import print_exc

class RedditscraperSpider:
    name = "redditScraper"
    allowed_domains = ["www.reddit.com"]
    start_urls = ["https://www.reddit.com/login/"]
    target_url = "https://www.reddit.com/r/ProgrammerHumor/new/"
    username = "Own_Astronaut_6220"
    password = "1Villageinthehole!"
    TIMEOUT = 5000  # Increased timeout value (5 seconds)
    SCROLL_LIMIT = 50  # Set your desired scroll limit

    def __init__(self):
        self.items_pipeline = RedditPipeline()

    def login(self, page):
        # TODO: Implement login logic
        page.fill('input[name="username"]', self.username)
        page.fill('input[name="password"]', self.password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

    def scroll_to_end(self, page):
        scroll_count = 0
        while scroll_count < self.SCROLL_LIMIT:
            old_height = page.evaluate('document.body.scrollHeight')
            page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
            page.wait_for_timeout(self.TIMEOUT)
            new_height = page.evaluate('document.body.scrollHeight')

            if new_height == old_height:
                break

            scroll_count += 1
        page.wait_for_load_state("networkidle")

    def extract_post_information(self, tree):
        posts = tree.css("div [data-testid='post-container']")
        for post in posts:
            checked_tags = (post.css("span"))
            tag_list = []
            for tag in checked_tags:
                tag_list.append(tag.text())
            if "promoted" not in tag_list:
                # Create a RedditItem instance for each post
                rank_element = post.css_first("div[id*='vote-arrows'] div")
                rank = rank_element.text() if rank_element is not None else ''

                comments_element = post.css_first('a[data-click-id="comments"] span')
                comments = comments_element.text() if comments_element is not None else ''

                # Check if the element with the specified selector exists before accessing its attributes
                img_url_element = post.css_first('img[alt="Post image"]')
                video_url_element = post.css_first('video source')
                url_element = img_url_element or video_url_element

                url = url_element.attributes.get('src', '') if url_element is not None else ''

                signature_element = post.css_first("h3")
                signature = signature_element.text() if signature_element is not None else ''

                posted_by_element = post.css_first('a[data-testid="post_author_link"]')
                posted_by = posted_by_element.text() if posted_by_element is not None else ''

                posted_when_element = post.css_first('span[data-testid="post_timestamp"]')
                posted_when = posted_when_element.text() if posted_when_element is not None else ''

                item = RedditItem(rank, comments, url, signature, posted_by, posted_when)
                self.items_pipeline.process_item(item)

    def run_spider(self):
        logging.basicConfig(level=logging.INFO)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            try:
                page.goto(self.start_urls[0])
                self.login(page)

                page.goto(self.target_url)
                self.scroll_to_end(page)

                html = page.content()
                tree = HTMLParser(html)

                self.extract_post_information(tree)

            except Exception as e:
                logging.error(f"An error occurred: {e}")
                print_exc()

            finally:
                context.close()
                # self.items_pipeline.save_items_to_csv()
                self.items_pipeline.save_items_to_db()

if __name__ == "__main__":
    spider = RedditscraperSpider()
    spider.run_spider()
