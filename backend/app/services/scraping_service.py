import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ScrapingService:
    async def fetch_url_content(self, url: str) -> str | None:
        """
        Fetches the content of a URL and extracts clean text.
        Returns the text content or None if fetching fails.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                # Use BeautifulSoup to parse the HTML and extract text
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove script and style elements
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                
                # Get text and clean it up
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = '\n'.join(chunk for chunk in chunks if chunk)

                return clean_text

        except httpx.RequestError as e:
            logger.error(f"Error while requesting {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while scraping {url}: {e}")
            return None

scraping_service = ScrapingService()
