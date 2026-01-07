import os
import requests
from dotenv import load_dotenv

load_dotenv()
LISTENNOTES_API_KEY = os.getenv("LISTENNOTES_API_KEY")

BASE_URL = "https://listen-api.listennotes.com/api/v2"
HEADERS = {"X-ListenAPI-Key": LISTENNOTES_API_KEY}


def search_podcast(query):
    try:
        url = f"{BASE_URL}/search?q={query}&type=podcast&language=English"
        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if not results:
                print("⚠️ No results found. Using fallback podcasts.")
                results = [
                    {"id": "4d3fe717742d4963a85562e9f84d8c79", "title_original": "Lex Fridman Podcast"},
                    {"id": "2d1b3f55e1b84f47adf01107ecb02d93", "title_original": "AI Today Podcast"},
                ]
            return results
        else:
            print(f"⚠️ Search failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error searching podcast: {e}")
        return []

def get_episodes(podcast_id):
    try:
        url = f"{BASE_URL}/podcasts/{podcast_id}?sort=recent_first"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("episodes", [])
        else:
            print(f"⚠️ Episodes fetch failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting episodes: {e}")
        return []

def get_audio_url(episode_id):
    try:
        url = f"{BASE_URL}/episodes/{episode_id}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            audio_url = data.get("audio")
            title = data.get("title")
            if not audio_url:
                print("⚠️ No audio URL found in episode data.")
            return audio_url, title
        else:
            print(f"⚠️ Episode fetch failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Error fetching audio: {e}")
        return None, None
