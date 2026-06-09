import requests
from bs4 import BeautifulSoup


def scrape_website(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"

        paragraphs = soup.find_all("p")
        content = " ".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
        )

        if not content:
            content = soup.get_text(" ", strip=True)

        content = " ".join(content.split())

        return {
            "title": title,
            "content": content[:5000]
        }

    except requests.exceptions.RequestException as e:
        print(f"Scraping Error: {e}")
        return None

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None