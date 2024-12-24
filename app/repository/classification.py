from typing import Tuple
from functools import lru_cache
import spacy
from toolz import curry
from app.utils.groq_client import create_chat_completion

@lru_cache(maxsize=128)
def classify_article(title: str, body: str) -> str:
    prompt = f"""
    Analyze this article and classify it into exactly one of these categories:
    - General News: News not related to terrorism
    - Historical Terror Event: Past terrorist incidents
    - Current Terror Event: Recent or ongoing terrorist incidents

    Use these guidelines:
    - Current: Events within the last month
    - Historical: Events older than a month
    - If unclear, classify as General News

    Title: {title}
    Body: {body}

    Return only the category name, nothing else.
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = create_chat_completion(messages)
        category = response.choices[0].message.content.strip()
        valid_categories = {
            "General News",
            "Historical Terror Event",
            "Current Terror Event"
        }
        return category if category in valid_categories else "General News"
    except Exception as e:
        print(f"Classification error: {e}")
        return "General News"

@curry
def extract_location_groq(title: str, body: str) -> str:
    prompt = f"""
    Extract the most specific location (city, region, or country) from this article.
    Focus on:
    1. Location of the main event
    2. Most specific location mentioned
    3. Locations in the title

    Title: {title}
    Body: {body}

    Return only the location name. If multiple locations, return the most relevant one.
    If no clear location, return 'Global'.
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = create_chat_completion(messages)
        location = response.choices[0].message.content.strip()
        return location if location.lower() not in ["unknown", "none", "multiple"] else "Global"
    except Exception as e:
        print(f"Location extraction error: {e}")
        return "Global"

@curry
def extract_location_spacy(text: str, nlp) -> str:
    try:
        doc = nlp(text)
        locations = []
        for ent in doc.ents:
            if ent.label_ == "GPE":
                locations.append((ent.text, 2))
            elif ent.label_ == "LOC":
                locations.append((ent.text, 1))
        if locations:
            return sorted(locations, key=lambda x: x[1], reverse=True)[0][0]
        return "Global"
    except Exception as e:
        print(f"spaCy extraction error: {e}")
        return "Global"

def get_nlp():
    return spacy.load('en_core_web_sm')

def extract_location(title: str, body: str) -> str:
    location = extract_location_groq(title, body)
    if location == "Global":
        nlp = get_nlp()
        combined_text = f"{title}. {body}"
        location = extract_location_spacy(combined_text, nlp)
    return location

def process_article_text(title: str, body: str) -> Tuple[str, str]:
    category = classify_article(title, body)
    location = "Global"
    if category in ["Historical Terror Event", "Current Terror Event"]:
        location = extract_location(title, body)
    return category, location