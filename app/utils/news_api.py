import requests
from app.db.elastic_search_db import get_elastic_client

API_KEY = "5a8e538e-9d6e-4730-81ee-abf12bf73c90"
BASE_URL = "https://eventregistry.org/api/v1/article/getArticles"

def fetch_articles_from_newsapi(keyword, page):
    payload = {
        "action": "getArticles",
        "keyword": keyword,
        "articlesPage": page,
        "articlesCount": 10,
        "articlesSortBy": "socialScore",
        "articlesSortByAsc": False,
        "dataType": ["news", "pr"],
        "forceMaxDataTimeWindow": 31,
        "resultType": "articles",
        "apiKey": API_KEY,
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", {}).get("results", [])
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []

def save_articles_to_elasticsearch(articles):
    client = get_elastic_client()
    for article in articles:
        doc = {
            "title": article.get("title"),
            "body": article.get("body"),
            "dateTime": article.get("dateTime"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("title", "Unknown"),
        }
        client.index(index=index_name, document=doc)