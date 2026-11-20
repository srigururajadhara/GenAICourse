
import requests
from bs4 import BeautifulSoup

# BBC News URL
url = "https://www.bbc.com/news"

# Normal browser User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

try:
    # Fetch the webpage
    response = requests.get(url, headers=headers, timeout=15)

    # Check HTTP status before parsing
    if response.status_code != 200:
        print(f"Failed to fetch page. Status: {response.status_code}")
        exit()

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find headline elements
    headline_elements = soup.select('[data-testid="card-headline"]')

    # Collect unique, non-empty headlines
    headlines = []
    seen = set()

    for element in headline_elements:
        headline = element.get_text(strip=True)

        if headline and headline not in seen:
            headlines.append(headline)
            seen.add(headline)

        if len(headlines) == 5:
            break

    # Print results
    print("\n===== TOP 5 BBC NEWS HEADLINES =====\n")

    if not headlines:
        print("No headlines found. The website structure may have changed.")
    else:
        for index, headline in enumerate(headlines, start=1):
            print(f"{index}. {headline}")

        if len(headlines) < 5:
            print(f"\nOnly {len(headlines)} unique headlines were found.")

except requests.exceptions.RequestException as error:
    print(f"Network error: {error}")
