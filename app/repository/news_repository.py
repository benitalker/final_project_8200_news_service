from datetime import datetime
from app.repository.classification import classify_article, extract_location
from app.repository.elastic_repository import save_article_to_elastic
from app.repository.geocoding import get_coordinates

def format_date(date_str):
    if not date_str:
        return datetime.now().isoformat()
    try:
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue
        return datetime.now().isoformat()
    except Exception as e:
        print(f"Date parsing error: {e}")
        return datetime.now().isoformat()

def process_and_store_article(article):
    try:
        title = article.get("title", "")
        body = article.get("body", "")
        date_time = format_date(article.get("dateTime", ""))
        url = article.get("url", "")
        source = article.get("source", {}).get("title", "Unknown")
        category = classify_article(title, body)
        if category in ["Historical Terror Event", "Current Terror Event"]:
            print('This article is historical or current')
            location = extract_location(title, body)
            print(f'location: {location}')
            if location and location.lower() != "global":
                coordinates = get_coordinates(location)
            else:
                location = "Global"
                coordinates = {"latitude": None, "longitude": None}
        else:
            location = "Global"
            coordinates = {"latitude": None, "longitude": None}
        processed_article = {
            "title": title,
            "body": body,
            "category": category,
            "location": location,
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
            "dateTime": date_time,
            "url": url,
            "source": source
        }
        save_article_to_elastic(processed_article)
        return processed_article
    except Exception as e:
        print(f"Error processing article: {e}")
        return None