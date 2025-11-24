# app/services/cache_manager.py
import time
from typing import Any, Optional

class CacheManager:
    def __init__(self):
        self._cache = {}
        self.default_ttl = 600  # 10 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        data = self._cache.get(key)
        if data and time.time() - data["timestamp"] < data["ttl"]:
            return data["value"]
        # Supprimer si expiré
        if data:
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Stocke une valeur dans le cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
    
    def clear(self):
        """Vide le cache"""
        self._cache.clear()
    
    def stats(self):
        """Retourne les statistiques du cache"""
        return {
            "total_entries": len(self._cache),
            "keys": list(self._cache.keys())
        }

# Instance globale
cache_manager = CacheManager()