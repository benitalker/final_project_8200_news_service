from groq import Groq
import time
from app.utils.config import GROQ_API_KEY

def get_groq_client():
    api_key = GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    return Groq(api_key=api_key)

def create_chat_completion(messages, model="llama3-8b-8192", retries=3):
    client = get_groq_client()
    models = [model, "llama3-groq-70b-8192-tool-use-preview", "llama3-groq-8b-8192-tool-use-preview", "gemma2-9b-it", "llama-3.1-8b-instant",
              "llama-3.2-11b-vision-preview", "llama-3.2-1b-preview", "llama-3.2-3b-preview", "llama-3.2-90b-vision-preview",
              "llama-3.3-70b-specdec", "llama-3.3-70b-versatile", "llama-guard-3-8b", "llama3-70b-8192",
              "llama3-8b-8192", "mixtral-8x7b-32768", "whisper-large-v3", "whisper-large-v3-turbo",]
    for retry in range(retries):
        for current_model in models:
            try:
                response = client.chat.completions.create(
                    messages=messages,
                    model=current_model,
                )
                return response
            except Exception as e:
                error_message = str(e)
                print(f"Error with model {current_model}: {error_message}")
                if "rate_limit_exceeded" in error_message:
                    try:
                        retry_after = float(
                            error_message.split("try again in ")[1].split("s")[0]
                        )
                        print(f"Rate limit reached. Retrying after {retry_after} seconds...")
                        time.sleep(retry_after)
                    except Exception:
                        print("Rate limit reached. Retrying after 2 seconds...")
                        time.sleep(2)
                else:
                    print(f"Retry {retry + 1}/{retries} failed for model {current_model}.")
    raise RuntimeError("All models failed after retries.")
