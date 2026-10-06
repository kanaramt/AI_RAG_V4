import os
import json
import requests
from typing import Optional, Any
from services.cache.base_cache import BaseCache

class UpstashRedisCache(BaseCache):
    def __init__(self, rest_url: str = None, rest_token: str = None):
        self.url = rest_url or os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = rest_token or os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.is_enabled = bool(self.url and self.token)

    def get(self, key: str) -> Optional[Any]:
        if not self.is_enabled:
            return None
        try:
            response = requests.get(f"{self.url}/get/{key}", headers=self.headers, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    try:
                        return json.loads(data["result"])
                    except json.JSONDecodeError:
                        return data["result"]
        except Exception as e:
            print(f"[Upstash] Get Error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if not self.is_enabled:
            return False
        try:
            val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            response = requests.post(
                f"{self.url}/set/{key}",
                headers=self.headers,
                json=val_str,
                timeout=2.0
            )
            if response.status_code == 200:
                requests.get(f"{self.url}/expire/{key}/{ttl}", headers=self.headers, timeout=2.0)
                return True
        except Exception as e:
            print(f"[Upstash] Set Error: {e}")
        return False

    def delete(self, key: str) -> bool:
        if not self.is_enabled:
            return False
        try:
            response = requests.get(f"{self.url}/del/{key}", headers=self.headers, timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False
