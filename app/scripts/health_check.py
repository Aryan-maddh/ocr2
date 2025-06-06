
import requests
import sys
import time
from typing import Dict, Any

def check_service_health(service_name: str, url: str, timeout: int = 10) -> Dict[str, Any]:
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "service": service_name,
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time": response.elapsed.total_seconds(),
            "status_code": response.status_code
        }
    except requests.exceptions.RequestException as e:
        return {
            "service": service_name,
            "status": "unhealthy",
            "error": str(e)
        }

def main():
    """Main health check function"""
    services = [
        ("API", "http://localhost:8000/health"),
        ("Database", "http://localhost:8000/db-health"),
        ("Redis", "http://localhost:8000/redis-health"),
        ("Ollama", "http://localhost:11434/api/tags"),
    ]
    
    all_healthy = True
    
    print("=== Service Health Check ===")
    for service_name, url in services:
        result = check_service_health(service_name, url)
        
        status_emoji = "✅" if result["status"] == "healthy" else "❌"
        print(f"{status_emoji} {result['service']}: {result['status']}")
        
        if result["status"] != "healthy":
            all_healthy = False
            if "error" in result:
                print(f"   Error: {result['error']}")
    
    if all_healthy:
        print("\n🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("\n⚠️  Some services are unhealthy!")
        sys.exit(1)

if __name__ == "__main__":
    main()