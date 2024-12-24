import logging
from app.db.elastic_search_db import news_mapping, create_index
from app.utils.scheduler import NewsScheduler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    try:
        # Create Elasticsearch index if it doesn't exist
        create_index(index_name="news_articles", mapping=news_mapping)

        # Initialize and run the scheduler
        scheduler = NewsScheduler(interval_minutes=2)
        scheduler.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    main()