import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict, Any
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException


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


class ApplyBoardScraper(WebScraper):
    """Custom scraper for ApplyBoard study destinations."""

    def __init__(self):
        super().__init__("https://www.applyboard.com")
        self.countries = {}
        self.driver = None
    
    def setup_driver(self):
        """Setup Selenium WebDriver (tries Firefox first, then Chrome)."""
        if self.driver:
            return self.driver
        
        try:
            print("🔧 Setting up Firefox WebDriver...")
            options = FirefoxOptions()
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Firefox(options=options)
            print("✓ Firefox WebDriver ready")
            return self.driver
        except Exception as e:
            print(f"Firefox not available: {e}")
            try:
                print("🔧 Trying Chrome WebDriver...")
                options = ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                self.driver = webdriver.Chrome(options=options)
                print("✓ Chrome WebDriver ready")
                return self.driver
            except Exception as e2:
                print(f"❌ Chrome also not available: {e2}")
                print("\n⚠️  Please install either Firefox or Chrome browser")
                return None
    
    def fetch_page_with_js(self, url: str, wait_for_selector: str = None, wait_time: int = 10) -> BeautifulSoup:
        """
        Fetch a page that requires JavaScript using Selenium.
        
        Args:
            url: URL to fetch
            wait_for_selector: CSS selector to wait for before returning
            wait_time: Maximum time to wait (seconds)
            
        Returns:
            BeautifulSoup object of the loaded page
        """
        driver = self.setup_driver()
        if not driver:
            return None
        
        try:
            print(f"🌐 Loading page with JavaScript support...")
            driver.get(url)
            
            if wait_for_selector:
                print(f"⏳ Waiting for content to load (selector: {wait_for_selector})...")
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
            else:
                # Default wait for articles to load
                print(f"⏳ Waiting for program cards to load...")
                time.sleep(3)  # Initial wait
                try:
                    WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                    )
                except TimeoutException:
                    print("⚠️  Timeout waiting for articles, continuing anyway...")
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            print("✓ Page loaded successfully")
            return soup
            
        except Exception as e:
            print(f"Error loading page with JavaScript: {e}")
            return None
    
    def close_driver(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("🔒 Browser closed")

    def get_study_destinations(self) -> Dict[str, str]:
        """
        Scrape the list of study destinations (countries) from the homepage.

        Returns:
            Dictionary of country names and their URLs
        """
        print("Fetching study destinations...")
        soup = self.fetch_page()

        if not soup:
            return {}

        countries = {}

        # Find the "Study Destinations" menu and its submenu items
        # Looking for links that match the country pattern
        country_links = soup.find_all("a", class_="elementor-sub-item")

        for link in country_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Filter for country links (e.g., /australia, /canada, etc.)
            if href and any(
                country in href.lower()
                for country in [
                    "australia",
                    "canada",
                    "ireland",
                    "germany",
                    "uk",
                    "usa",
                ]
            ):
                countries[text] = href

        self.countries = countries
        return countries

    def display_country_menu(self) -> str:
        """
        Display country options in terminal and get user selection.

        Returns:
            Selected country URL
        """
        if not self.countries:
            self.get_study_destinations()

        if not self.countries:
            print("No countries found!")
            return None

        print("\n" + "=" * 50)
        print("📚 STUDY DESTINATIONS")
        print("=" * 50)

        country_list = list(self.countries.items())
        for idx, (country, url) in enumerate(country_list, 1):
            print(f"{idx}. {country}")

        print("=" * 50)

        while True:
            try:
                choice = input("\n🌍 Select a country (enter number): ").strip()
                idx = int(choice) - 1

                if 0 <= idx < len(country_list):
                    selected_country, selected_url = country_list[idx]
                    print(f"\n✓ Selected: {selected_country}")
                    print(f"📍 URL: {selected_url}\n")
                    return selected_country, selected_url
                else:
                    print(f"❌ Please enter a number between 1 and {len(country_list)}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                return None, None

    def get_explore_programs_link(self, country_url: str) -> str:
        """
        Get the "Explore more programs" link from a country page.

        Args:
            country_url: URL of the country page

        Returns:
            URL of the programs page
        """
        print(f"Fetching country page: {country_url}")
        soup = self.fetch_page(country_url)

        if not soup:
            return None

        # Find "Explore more programs" link
        explore_links = soup.find_all("a", class_="elementor-button")

        for link in explore_links:
            text = link.get_text(strip=True).lower()
            if "explore" in text and "program" in text:
                href = link.get("href", "")
                if href:
                    print(f"✓ Found programs link: {href}")
                    return href

        # Alternative: look for any link with search parameters
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/search?" in href and "filter" in href:
                print(f"✓ Found programs link: {href}")
                return href

        print("❌ Could not find 'Explore more programs' link")
        return None

    def get_total_items(self, soup: BeautifulSoup) -> int:
        """
        Get the total number of items available from pagination info.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            Total number of items
        """
        try:
            # Find the pagination text that shows "1 - 12 of 830 items"
            pagination_text = soup.find("span", {"data-testid": "temp"})
            if pagination_text:
                text = pagination_text.get_text()
                # Extract total number (e.g., "1 - 12 of 830 items" -> 830)
                import re

                match = re.search(r"of (\d+) items", text)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Could not determine total items: {e}")
        return 0

    def scrape_program_card(self, article) -> Dict[str, Any]:
        """
        Extract data from a single program card.

        Args:
            article: BeautifulSoup element of the program card

        Returns:
            Dictionary containing program data
        """
        program = {}

        try:
            # School name
            school_h3 = article.find("h3", class_="css-1a91344")
            if school_h3:
                program["school_name"] = school_h3.get_text(strip=True)

            # School URL
            school_link = article.find("a", href=True, class_="css-cxyr4a")
            if school_link and "/schools/" in school_link["href"]:
                program["school_url"] = school_link["href"]

            # Degree type
            degree_div = article.find("div", class_="css-eqx0xi")
            if degree_div:
                program["degree_type"] = degree_div.get_text(strip=True)

            # Program name
            program_h2 = article.find("h2", class_="css-7iklpx")
            if program_h2:
                program["program_name"] = program_h2.get_text(strip=True)

            # Program URL
            program_link = article.find("a", href=True)
            if program_link and "/programs/" in program_link.get("href", ""):
                program["program_url"] = program_link["href"]

            # Extract details from the dl (definition list)
            dl = article.find("dl", class_="css-1d44v5m")
            if dl:
                details = dl.find_all("div", class_="css-1afznku")
                for detail in details:
                    dt = detail.find("dt")
                    dd = detail.find("dd")
                    if dt and dd:
                        key = dt.get_text(strip=True).lower().replace(" ", "_")
                        value = dd.get_text(strip=True)
                        program[key] = value

            # Success chance
            success_div = article.find("div", class_="css-koraoo")
            if success_div and success_div.get_text(strip=True) in [
                "High",
                "Medium",
                "Low",
            ]:
                program["success_chance"] = success_div.get_text(strip=True)

            # Available intakes
            intakes = []
            intake_divs = article.find_all("div", class_="css-koraoo")
            for div in intake_divs:
                text = div.get_text(strip=True)
                # Check if it matches date pattern (e.g., "Mar 2026")
                if any(
                    month in text
                    for month in [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ]
                ):
                    if text not in intakes:
                        intakes.append(text)
            if intakes:
                program["available_intakes"] = intakes

            # Check for special features
            features = []
            feature_spans = article.find_all("span", class_="css-1wftnvw")
            for span in feature_spans:
                feature = span.get_text(strip=True)
                if feature:
                    features.append(feature)
            if features:
                program["features"] = features

        except Exception as e:
            print(f"Error parsing program card: {e}")

        return program

    def scrape_programs_page(
        self, programs_url: str, max_items: int = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape program data from the programs listing page.

        Args:
            programs_url: URL of the programs page
            max_items: Maximum number of items to scrape (None for all)

        Returns:
            List of program data dictionaries
        """
        print(f"\nFetching programs page: {programs_url}")

        # Modify URL to show 48 items per page
        if "?" in programs_url:
            if "page[size]=" not in programs_url:
                programs_url += "&page[size]=48"
            else:
                programs_url = programs_url.replace("page[size]=12", "page[size]=48")

        soup = self.fetch_page_with_js(programs_url)

        if not soup:
            return []

        # Get total items
        total_items = self.get_total_items(soup)
        print(f"📊 Total programs available: {total_items}")

        if max_items is None:
            # Ask user how many to fetch
            print("\n" + "=" * 50)
            while True:
                try:
                    choice = (
                        input(
                            f"How many programs to scrape? (max {total_items}, or 'all'): "
                        )
                        .strip()
                        .lower()
                    )
                    if choice == "all":
                        max_items = total_items
                        break
                    else:
                        max_items = int(choice)
                        if 0 < max_items <= total_items:
                            break
                        else:
                            print(
                                f"❌ Please enter a number between 1 and {total_items}"
                            )
                except ValueError:
                    print("❌ Please enter a valid number or 'all'")
                except KeyboardInterrupt:
                    print("\n\n👋 Exiting...")
                    return []

        print(f"🎯 Will scrape {max_items} programs")
        print("=" * 50 + "\n")

        all_programs = []
        page_num = 1
        items_per_page = 48

        while len(all_programs) < max_items:
            print(f"📄 Scraping page {page_num}...")

            # Parse current page
            articles = soup.find_all("article", class_="css-1v3njm")
            print(f"   Found {len(articles)} programs on this page")

            for article in articles:
                if len(all_programs) >= max_items:
                    break

                program = self.scrape_program_card(article)
                if program:
                    all_programs.append(program)
                    print(
                        f"   ✓ Scraped: {program.get('program_name', 'Unknown')[:60]}..."
                    )

            # Check if we need to fetch next page
            if len(all_programs) >= max_items or len(all_programs) >= total_items:
                break

            # Build next page URL
            page_num += 1
            if "page[number]=" in programs_url:
                next_url = programs_url.replace(
                    f"page[number]={page_num-1}", f"page[number]={page_num}"
                )
            else:
                separator = "&" if "?" in programs_url else "?"
                next_url = programs_url + f"{separator}page[number]={page_num}"

            print(f"   Fetching next page...")
            soup = self.fetch_page_with_js(next_url)
            if not soup:
                break

        print(f"\n✅ Total programs scraped: {len(all_programs)}")
        return all_programs


# Example usage
if __name__ == "__main__":
    # Create ApplyBoard scraper
    scraper = ApplyBoardScraper()

    # Step 1: Get study destinations
    countries = scraper.get_study_destinations()

    if not countries:
        print("❌ Could not fetch study destinations")
        exit(1)

    # Step 2: Display menu and get user selection
    selected_country, country_url = scraper.display_country_menu()

    if not country_url:
        print("No country selected. Exiting...")
        exit(0)

    # Step 3: Get the "Explore more programs" link
    programs_url = scraper.get_explore_programs_link(country_url)

    if not programs_url:
        print("❌ Could not find programs link")
        exit(1)

    # Step 4: Scrape programs page
    programs = scraper.scrape_programs_page(programs_url)

    if programs:
        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"{selected_country.lower().replace(' ', '_')}_programs_{timestamp}.json"
        )
        scraper.save_to_json(programs, filename)

        print("\n" + "=" * 50)
        print("✅ SCRAPING COMPLETE")
        print("=" * 50)
        print(f"📁 Data saved to: {filename}")
        print(f"📊 Total programs: {len(programs)}")
    else:
        print("\n❌ No programs were scraped")
    scraper.close_driver()
