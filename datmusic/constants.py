import os

__version__ = "1.2.0"
DATMUSIC_API_ENDPOINT = os.getenv("DATMUSIC_API_ENDPOINT", "https://datmusic-api.dev/search/")
INLINE_QUERY_CACHE_TIME = 12 * 30 * 24 * 60 * 60; # 1 year