import os
from typing import List
from langchain.tools import tool
import dotenv
import requests

_unsplash_service = None

class UnsplashAPI:
    def __init__(self):
        dotenv.load_dotenv()
        self.base_url = "https://api.unsplash.com/"
        self.client_id = os.getenv("UNSPLASH_ACCESS_KEY")

    def search_photos(self, query: str, page_size: int = 5) -> List[dict]:
        '''
        search photos

        args:
        query: search keyword
        page_size: page size
        '''
        url = f'{self.base_url}search/photos'

        params = {
            "query": query,
            "per_page": page_size,
            "client_id": self.client_id,
        }

        response = requests.get(url, params=params)
        data = response.json()
        result = data.get("results", [])

        photos = []
        for photo in result:
            photos.append(
                {
                    "url": photo.get("urls", {}).get("regular"),
                }
            )
        return photos

def get_unsplash_service():
    global _unsplash_service
    if _unsplash_service is None:
        _unsplash_service = UnsplashAPI()
    return _unsplash_service