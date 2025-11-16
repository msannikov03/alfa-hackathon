import httpx
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ScrapingService:
    async def fetch_url_content(self, url: str) -> Dict[str, Any]:
        """
        Fetches the content of a URL and extracts clean text.
        Returns dict with {success: bool, content: str | None, error: str | None, error_type: str | None}
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

                return {
                    "success": True,
                    "content": clean_text,
                    "error": None,
                    "error_type": None
                }

        except httpx.TimeoutException:
            error_msg = "Сайт не отвечает (превышен timeout)"
            logger.error(f"Timeout while requesting {url}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "timeout"
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                error_msg = "Доступ запрещен (сайт блокирует автоматический доступ)"
            elif e.response.status_code == 404:
                error_msg = "Страница не найдена"
            elif e.response.status_code >= 500:
                error_msg = "Ошибка на сервере сайта"
            else:
                error_msg = f"HTTP ошибка {e.response.status_code}"
            logger.error(f"HTTP error {e.response.status_code} while requesting {url}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "http_error"
            }
        except httpx.RequestError as e:
            error_msg = "Ошибка подключения к сайту"
            logger.error(f"Request error while requesting {url}: {e}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "connection_error"
            }
        except Exception as e:
            error_msg = "Неожиданная ошибка при обработке сайта"
            logger.error(f"Unexpected error while scraping {url}: {e}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "unknown_error"
            }

    async def fetch_telegram_channel_content(self, channel_username: str) -> Dict[str, Any]:
        """
        Fetches recent posts from a public Telegram channel via web interface.

        Args:
            channel_username: Telegram channel username (without @)

        Returns:
            dict with {success: bool, content: str | None, error: str | None, error_type: str | None}
        """
        # Remove @ if present
        channel_username = channel_username.lstrip('@')

        # Telegram public channel web URL
        url = f"https://t.me/s/{channel_username}"

        logger.info(f"Fetching Telegram channel: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'lxml')

                # Telegram message divs have class 'tgme_widget_message_text'
                messages = soup.find_all('div', class_='tgme_widget_message_text')

                if not messages:
                    logger.warning(f"No messages found for channel {channel_username}")
                    return {
                        "success": False,
                        "content": None,
                        "error": "Канал не найден или пуст",
                        "error_type": "no_content"
                    }

                # Extract text from recent messages (limit to last 10)
                recent_posts = []
                for msg in messages[:10]:
                    text = msg.get_text(strip=True)
                    if text:
                        recent_posts.append(text)

                combined_text = '\n\n---\n\n'.join(recent_posts)
                logger.info(f"Successfully fetched {len(recent_posts)} messages from {channel_username}")

                return {
                    "success": True,
                    "content": combined_text,
                    "error": None,
                    "error_type": None
                }

        except httpx.TimeoutException:
            error_msg = "Telegram не отвечает (превышен timeout)"
            logger.error(f"Timeout while requesting Telegram channel {channel_username}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "timeout"
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = f"Канал @{channel_username} не найден"
            else:
                error_msg = f"Ошибка доступа к каналу (HTTP {e.response.status_code})"
            logger.error(f"HTTP error {e.response.status_code} while requesting Telegram channel {channel_username}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "http_error"
            }
        except httpx.RequestError as e:
            error_msg = "Ошибка подключения к Telegram"
            logger.error(f"Request error while requesting Telegram channel {channel_username}: {e}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "connection_error"
            }
        except Exception as e:
            error_msg = "Неожиданная ошибка при обработке канала"
            logger.error(f"Unexpected error while scraping Telegram channel {channel_username}: {e}")
            return {
                "success": False,
                "content": None,
                "error": error_msg,
                "error_type": "unknown_error"
            }

scraping_service = ScrapingService()
