# main_script.py
from items import RedditItem
from pipelines import RedditPipeline
from spiders import RedditscraperSpider

if __name__ == "__main__":
    spider = RedditscraperSpider()
    spider.run_spider()
