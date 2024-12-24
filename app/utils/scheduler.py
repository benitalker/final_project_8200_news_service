from functools import wraps
import time
import logging
from typing import Optional, List, Dict
import schedule
from toolz import pipe, curry
from app.repository.news_repository import process_and_store_article
from app.utils.news_api import fetch_articles_from_newsapi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: int = 5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    logger.warning(f"Attempt {retries} failed, retrying in {delay} seconds...")
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


@curry
def filter_valid_articles(articles: List[Dict]) -> List[Dict]:
    return [
        article for article in articles
        if article.get("title") and article.get("body")
    ]


@curry
def process_articles(articles: List[Dict]) -> List[Optional[Dict]]:
    return [process_and_store_article(article) for article in articles]


@retry_on_failure(max_retries=3)
def fetch_and_process_news(page: int = 1, keywords: str = "terror attack") -> None:
    logger.info(f"Fetching news articles from page {page}...")

    # Use functional composition with toolz
    processed_articles = pipe(
        fetch_articles_from_newsapi(keywords, page),
        filter_valid_articles,
        process_articles
    )

    # Filter out None values (failed processing)
    successful_articles = [a for a in processed_articles if a is not None]

    logger.info(f"Successfully processed {len(successful_articles)} articles")
    return len(successful_articles)


class NewsScheduler:
    def __init__(self, interval_minutes: int = 2):
        self.current_page = 1
        self.interval_minutes = interval_minutes

    def run(self):
        logger.info("Starting news scheduler...")
        schedule.every(self.interval_minutes).minutes.do(self._scheduled_task)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def _scheduled_task(self):
        try:
            articles_count = fetch_and_process_news(self.current_page)
            if articles_count == 0:
                logger.info("No articles found, resetting to page 1")
                self.current_page = 1
            else:
                self.current_page += 1
        except Exception as e:
            logger.error(f"Error in scheduled task: {str(e)}")
            self.current_page = 1  # Reset on error


if __name__ == "__main__":
    scheduler = NewsScheduler(interval_minutes=2)
    scheduler.run()