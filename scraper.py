import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict, Any


class WebScraper:
    """A flexible web scraper that saves data to JSON format."""

    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        """
        Initialize the scraper.

        Args:
            base_url: The base URL to scrape
            headers: Optional headers for requests (user agent, etc.)
        """
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.data = []

    def fetch_page(self, url: str = None) -> BeautifulSoup:
        """
        Fetch a webpage and return BeautifulSoup object.

        Args:
            url: URL to fetch (uses base_url if None)

        Returns:
            BeautifulSoup object of the page
        """
        target_url = url or self.base_url

        try:
            response = requests.get(target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching {target_url}: {e}")
            return None

    def scrape_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract data from the page. Override this method for custom scraping logic.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of dictionaries containing scraped data
        """
        # Example: Scrape all article titles and links
        results = []

        # Customize these selectors based on your target website
        articles = soup.find_all("article")  # Change selector as needed

        for article in articles:
            item = {}

            # Example extractions - customize based on your needs
            title_tag = article.find("h2") or article.find("h3")
            if title_tag:
                item["title"] = title_tag.get_text(strip=True)

            link_tag = article.find("a")
            if link_tag and link_tag.get("href"):
                item["link"] = link_tag["href"]

            description_tag = article.find("p")
            if description_tag:
                item["description"] = description_tag.get_text(strip=True)

            if item:  # Only add if we found something
                results.append(item)

        return results

    def save_to_json(self, data: List[Dict[str, Any]], filename: str = None):
        """
        Save scraped data to JSON file.

        Args:
            data: List of dictionaries to save
            filename: Output filename (auto-generated if None)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.json"

        output = {
            "scraped_at": datetime.now().isoformat(),
            "source_url": self.base_url,
            "total_items": len(data),
            "data": data,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"✓ Data saved to {filename}")
        print(f"✓ Total items scraped: {len(data)}")

    def run(self, save_file: str = None):
        """
        Run the complete scraping process.

        Args:
            save_file: Optional filename for output
        """
        print(f"Starting scrape of {self.base_url}...")

        soup = self.fetch_page()
        if not soup:
            print("Failed to fetch page!")
            return

        print("Page fetched successfully. Extracting data...")
        data = self.scrape_data(soup)

        if data:
            self.save_to_json(data, save_file)
        else:
            print("No data found. Check your selectors!")


# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage
    # Replace with your target URL
    scraper = WebScraper("https://example.com")
    scraper.run()

    # Example 2: Custom scraping with specific selectors
    # Uncomment and modify as needed:
    """
    scraper = WebScraper("https://your-target-site.com")
    soup = scraper.fetch_page()
    
    if soup:
        # Custom extraction logic
        custom_data = []
        
        # Example: Extract specific elements
        items = soup.select('.item-class')  # CSS selector
        
        for item in items:
            data_item = {
                'title': item.select_one('.title-class').get_text(strip=True),
                'price': item.select_one('.price-class').get_text(strip=True),
                'url': item.find('a')['href']
            }
            custom_data.append(data_item)
        
        scraper.save_to_json(custom_data, 'custom_output.json')
    """
