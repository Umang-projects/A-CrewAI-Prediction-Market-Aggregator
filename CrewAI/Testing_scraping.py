# scraping_tools.py

import os
import json
import requests
from crewai.tools import tool

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@tool("Polymarket Scraper Tool")
def polymarket_scraper_tool() -> list[dict]:
    """Scrapes the top markets from Polymarket and returns them as a list of dictionaries."""
    url = "https://gamma-api.polymarket.com/markets"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, params={"limit": 10})
        r.raise_for_status()
        return [
            {"product": m.get("question", "N/A"), "price": m.get("last_price", 0), "site": "Polymarket"}
            for m in r.json()
        ]
    except Exception as exc:
        return [{"site": "Polymarket", "error": str(exc)}]

@tool("Manifold Markets Scraper Tool")
def manifold_scraper_tool() -> list[dict]:
    """Scrapes active markets from Manifold Markets and returns them as a list of dictionaries."""
    try:
        url = "https://manifold.markets/api/v0/markets?limit=100"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return [
            {'product': m.get('question', 'N/A'), 'price': m.get('probability', 0), 'site': 'Manifold'}
            for m in response.json()
        ]
    except Exception as e:
        return [{"site": "Manifold", "error": str(e)}]

@tool("PredictIt Scraper Tool")
def predictit_scraper_tool() -> list[dict]:
    """Scrapes all markets from PredictIt and returns them as a list of dictionaries."""
    try:
        url = "https://www.predictit.org/api/marketdata/all/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        markets = response.json().get('markets', [])
        return [
            {'product': m.get('name', 'N/A'), 'price': m.get('contracts', [{}])[0].get('lastTradePrice', 0), 'site': 'PredictIt'}
            for m in markets
        ]
    except Exception as e:
        return [{"site": "PredictIt", "error": str(e)}]

@tool("JSON Data Saver Tool")
def save_json_tool(data: list[dict], output_file: str) -> str:
    """Saves a list of dictionaries to a specified JSON file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return f"Successfully saved {len(data)} records to {output_file}."
    except Exception as e:
        return f"Error saving data to {output_file}: {e}"