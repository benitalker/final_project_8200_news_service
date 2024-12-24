import logging
from app.db.elastic_search_db import news_mapping, create_index
from app.utils.scheduler import NewsScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        create_index(index_name="news_articles", mapping=news_mapping)
        scheduler = NewsScheduler(interval_minutes=2)
        scheduler.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()