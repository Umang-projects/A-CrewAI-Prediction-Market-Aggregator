import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd # Using pandas is great for creating a clean CSV


# It's a web scraping best practice to identify your script with a User-Agent header.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
def fetch_polymarket() -> list[dict]:
    """Scrapes the top 10 markets from Polymarket's (old) public API.""" # <-- FIX #1
    url = "https://gamma-api.polymarket.com/markets"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, params={"limit": 10})
        r.raise_for_status()
        return [
            {
                "product": m.get("question", "N/A"),
                "price":   m.get("last_price", 0),
                "site":    "Polymarket"
            }
            for m in r.json()
        ]
    except Exception as exc:
        return [{"site": "Polymarket", "error": str(exc)}]

def scrape_manifold():
    """
    Scrapes active markets from Manifold Markets via its public API.
    Like Polymarket, this site is dynamic, so calling the API is the best method.
    """
    print("Scraping Manifold Markets...")
    try:
        url = "https://manifold.markets/api/v0/markets?limit=100"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        raw_data = response.json()

        unified_products = [{'product': m.get('question', 'N/A'), 'price': m.get('probability', 0), 'site': 'Manifold'} for m in raw_data]
        print(f"  > Found {len(unified_products)} markets.")
        return unified_products

    except Exception as e:
        print(f"  > FAILED to scrape Manifold: {e}")
        return []

def scrape_predictit():
    """
    Scrapes all markets from PredictIt via its public API.
    This is the most reliable method for this site as well.
    """
    print("Scraping PredictIt...")
    try:
        url = "https://www.predictit.org/api/marketdata/all/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        raw_data = response.json()

        unified_products = [{'product': m.get('name', 'N/A'), 'price': m.get('contracts', [{}])[0].get('lastTradePrice', 0), 'site': 'PredictIt'} for m in raw_data.get('markets', [])]
        print(f"  > Found {len(unified_products)} markets.")
        return unified_products

    except Exception as e:
        print(f"  > FAILED to scrape PredictIt: {e}")
        return []

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Scrape data from each site
    polymarket_data = fetch_polymarket()
    manifold_data = scrape_manifold()
    predictit_data = scrape_predictit()

    # 2. Combine all the data into a single list
    all_data = polymarket_data + manifold_data + predictit_data
    print(f"\nTotal markets found across all sites: {len(all_data)}")

    # 3. Create an output directory
    os.makedirs("output", exist_ok=True)

    # 4. Save the combined data to a single JSON file
    json_filename = "C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/combined_data.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
    print(f"📄 Successfully saved combined data to {json_filename}")

    # 5. (Bonus) Save the combined data to a CSV file for easy viewing
    if all_data:
        csv_filename = "C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/unified_board.csv"
        # Using pandas is the easiest and most robust way to create a CSV
        df = pd.DataFrame(all_data)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"📄 Successfully saved unified board to {csv_filename}")

    print("\n✅ Scraping process complete!")