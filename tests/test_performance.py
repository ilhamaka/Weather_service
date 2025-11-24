# test_performance.py
import requests
import time

def test_cache_performance():
    """Test les performances du cache"""
    base_url = "http://localhost:5000"
    
    print("⚡ Testing Cache Performance...")
    print("=" * 40)
    
    # Première requête
    print("1. Première requête (API + DB)...")
    start_time = time.time()
    response1 = requests.get(f"{base_url}/weather?depart=Paris&arrivee=London")
    first_call_time = time.time() - start_time
    
    data1 = response1.json()
    print(f"   ⏱️  Temps: {first_call_time:.3f}s")
    print(f"   📍 Source: {data1['data']['depart']['source']}")
    
    # Deuxième requête (devrait utiliser le cache)
    print("\n2. Deuxième requête (Cache)...")
    start_time = time.time()
    response2 = requests.get(f"{base_url}/weather?depart=Paris&arrivee=London")
    second_call_time = time.time() - start_time
    
    data2 = response2.json()
    print(f"   ⏱️  Temps: {second_call_time:.3f}s")
    print(f"   📍 Source: {data2['data']['depart']['source']}")
    
    print("\n" + "=" * 40)
    print(f"📈 Amélioration: {first_call_time/second_call_time:.1f}x plus rapide")
    
    # Vérifier que le cache est utilisé
    if data2["data"]["depart"]["source"] == "cache_memoire":
        print("✅ Cache mémoire fonctionne correctement")
    else:
        print("❌ Cache mémoire ne fonctionne pas")

if __name__ == "__main__":
    test_cache_performance()