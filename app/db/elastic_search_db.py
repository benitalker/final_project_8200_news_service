from elasticsearch import Elasticsearch

def get_elastic_client():
    return Elasticsearch(
        hosts=["http://localhost:9200"],
        basic_auth=("elastic", "3uDiv6AS"),
        verify_certs=False,
    )

def create_index(index_name="news_articles", mapping=None):
    try:
        client = get_elastic_client()
        if client.indices.exists(index=index_name):
            print(f"Index '{index_name}' already exists.")
            return
        client.indices.create(index=index_name, body=mapping)
        print(f"Index '{index_name}' created successfully.")
    except Exception as e:
        print(f"Error creating index '{index_name}': {e}")

news_mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "body": {"type": "text"},
            "category": {"type": "keyword"},
            "location": {"type": "keyword"},
            "dateTime": {
                "type": "date",
                "format": "strict_date_optional_time||epoch_millis||yyyy-MM-dd'T'HH:mm:ss'Z'||yyyy-MM-dd"
            },
            "source": {"type": "keyword"},
            "url": {"type": "keyword"},
            "latitude": {"type": "float"},
            "longitude": {"type": "float"}
        }
    }
}