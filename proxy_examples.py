#!/usr/bin/env python3
"""
Example usage of the scraper with proxy support
"""

import requests
import json

# Example 1: HTTP Proxy with authentication
def test_http_proxy_with_auth():
    """Test scraping with HTTP proxy and authentication"""
    url = "http://localhost:6090/webhook/scrape"

    payload = {
        "limit": 3,
        "proxy": {
            "server": "http://proxy.example.com:8080",
            "username": "your_username",
            "password": "your_password"
        }
    }

    response = requests.post(url, json=payload)
    return response.json()


# Example 2: SOCKS5 Proxy without authentication
def test_socks5_proxy():
    """Test scraping with SOCKS5 proxy"""
    url = "http://localhost:6090/webhook/scrape"

    payload = {
        "limit": 5,
        "proxy": {
            "server": "socks5://proxy.example.com:1080"
        }
    }

    response = requests.post(url, json=payload)
    return response.json()


# Example 3: HTTP Proxy without authentication
def test_http_proxy():
    """Test scraping with HTTP proxy without auth"""
    url = "http://localhost:6090/webhook/scrape"

    payload = {
        "limit": 2,
        "proxy": {
            "server": "http://proxy.example.com:3128"
        }
    }

    response = requests.post(url, json=payload)
    return response.json()


# Example 4: No proxy (backwards compatibility)
def test_no_proxy():
    """Test scraping without proxy (old behavior)"""
    url = "http://localhost:6090/webhook/scrape"

    payload = {
        "limit": 1
    }

    response = requests.post(url, json=payload)
    return response.json()


# Example 5: GET endpoint (backwards compatibility)
def test_get_endpoint():
    """Test GET endpoint without proxy"""
    url = "http://localhost:6090/webhook/scrape?limit=2"

    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    print("Proxy Examples for Sahibinden Scraper")
    print("=" * 50)

    # Note: These examples assume the webhook server is running on localhost:6090
    # Start the server with: python webhook_server.py

    print("\n1. HTTP Proxy with Authentication:")
    print("POST /webhook/scrape")
    print(json.dumps({
        "limit": 3,
        "proxy": {
            "server": "http://proxy.example.com:8080",
            "username": "your_username",
            "password": "your_password"
        }
    }, indent=2))

    print("\n2. SOCKS5 Proxy:")
    print("POST /webhook/scrape")
    print(json.dumps({
        "limit": 5,
        "proxy": {
            "server": "socks5://proxy.example.com:1080"
        }
    }, indent=2))

    print("\n3. HTTP Proxy without Authentication:")
    print("POST /webhook/scrape")
    print(json.dumps({
        "limit": 2,
        "proxy": {
            "server": "http://proxy.example.com:3128"
        }
    }, indent=2))

    print("\n4. No Proxy (backwards compatibility):")
    print("POST /webhook/scrape")
    print(json.dumps({
        "limit": 1
    }, indent=2))

    print("\n5. GET endpoint (backwards compatibility):")
    print("GET /webhook/scrape?limit=2")

    print("\nProxy server formats supported:")
    print("- HTTP: http://host:port")
    print("- HTTPS: https://host:port")
    print("- SOCKS5: socks5://host:port")
    print("- SOCKS4: socks4://host:port")
