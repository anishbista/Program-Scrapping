import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import time
import os
from dotenv import load_dotenv
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
        self.is_logged_in = False

        # Load environment variables
        load_dotenv()
        self.email = os.getenv("APPLYBOARD_EMAIL")
        self.password = os.getenv("APPLYBOARD_PASSWORD")

    def setup_driver(self):
        """Setup Selenium WebDriver (tries Firefox first, then Chrome)."""
        if self.driver:
            return self.driver

        try:
            print("🔧 Setting up Firefox WebDriver...")
            options = FirefoxOptions()
            # options.add_argument("--headless")  # Run in background
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Firefox(options=options)
            print("✓ Firefox WebDriver ready")
            return self.driver
        except Exception as e:
            print(f"Firefox not available: {e}")
            try:
                print("🔧 Trying Chrome WebDriver...")
                options = ChromeOptions()
                # options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = webdriver.Chrome(options=options)
                print("✓ Chrome WebDriver ready")
                return self.driver
            except Exception as e2:
                print(f"❌ Chrome also not available: {e2}")
                print("\n⚠️  Please install either Firefox or Chrome browser")
                return None

    def login(self, email: str = None, password: str = None) -> bool:
        """
        Log in to ApplyBoard using credentials from .env file or provided parameters.

        Args:
            email: User's email (uses .env if not provided)
            password: User's password (uses .env if not provided)

        Returns:
            True if login successful, False otherwise
        """
        driver = self.setup_driver()
        if not driver:
            return False

        # Use provided credentials or fall back to .env
        if not email:
            email = self.email
        if not password:
            password = self.password

        # Validate credentials are available
        if not email or not password:
            print("❌ Error: Email or password not found in .env file")
            print(
                "Please add APPLYBOARD_EMAIL and APPLYBOARD_PASSWORD to your .env file"
            )
            return False

        try:
            print("\n🔐 Logging in to ApplyBoard...")
            login_url = "https://accounts.applyboard.com/"
            driver.get(login_url)

            print("⏳ Waiting for login page to load...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "okta-sign-in"))
            )

            print("📝 Entering credentials...")
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "identifier"))
            )
            email_field.clear()
            email_field.send_keys(email)

            password_field = driver.find_element(By.NAME, "credentials.passcode")
            password_field.clear()
            password_field.send_keys(password)

            print("🚀 Submitting login form...")
            login_button = driver.find_element(
                By.CSS_SELECTOR, "input[type='submit'][value='Log In']"
            )
            login_button.click()

            print("⏳ Waiting for authentication...")
            time.sleep(3)
            current_url = driver.current_url

            if (
                "accounts.applyboard.com" in current_url
                and "error" not in current_url.lower()
            ):
                try:
                    error_element = driver.find_element(
                        By.CSS_SELECTOR, ".o-form-error-container"
                    )
                    if error_element.text:
                        print(f"❌ Login failed: {error_element.text}")
                        return False
                except:
                    pass
                time.sleep(5)
                current_url = driver.current_url

            if (
                "accounts.applyboard.com" not in current_url
                or "home" in current_url.lower()
            ):
                print("✅ Login successful!")
                self.is_logged_in = True
                print("🏠 Navigating to homepage...")
                driver.get("https://www.applyboard.com")
                time.sleep(2)
                return True
            else:
                print("❌ Login may have failed. Please check your credentials.")
                print(f"Current URL: {current_url}")
                return False

        except TimeoutException as e:
            print(f"❌ Timeout during login: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False

    def fetch_page_with_js(
        self, url: str, wait_for_selector: str = None, wait_time: int = 10
    ) -> BeautifulSoup:
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
                print(
                    f"⏳ Waiting for content to load (selector: {wait_for_selector})..."
                )
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
            soup = BeautifulSoup(page_source, "lxml")
            print("✓ Page loaded successfully")
            return soup

        except Exception as e:
            print(f"Error loading page with JavaScript: {e}")
            return None

    def close_driver(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"⚠️ Error closing driver: {e}")
            finally:
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

    def extract_program_url_from_card(self, article) -> str:
        """
        Extract just the program URL from a listing card.

        Args:
            article: BeautifulSoup element of the program card

        Returns:
            Program detail page URL
        """
        # Try multiple strategies to find the program link
        detail_link = None

        # Strategy 1: Look for link with specific class in div with class 'css-0'
        div = article.find("div", class_="css-0")
        if div:
            detail_link = div.find("a", class_="css-cxyr4a", href=True)

        # Strategy 2: Look for any link with class containing 'css-cxyr4a'
        if not detail_link:
            detail_link = article.find(
                "a", class_=lambda x: x and "css-cxyr4a" in x if x else False, href=True
            )

        # Strategy 3: Look for link with target="_blank" that goes to /schools/
        if not detail_link:
            all_links = article.find_all("a", href=True, attrs={"target": "_blank"})
            for link in all_links:
                if "/schools/" in link.get("href", "") and "/programs/" in link.get(
                    "href", ""
                ):
                    detail_link = link
                    break

        # Strategy 4: Use aria-label to find the right link
        if not detail_link:
            aria_label = article.get("aria-label", "")
            if aria_label.startswith("View program"):
                # Find any link with href containing /programs/
                all_links = article.find_all("a", href=True)
                for link in all_links:
                    if "/programs/" in link.get("href", ""):
                        detail_link = link
                        break

        if not detail_link or not detail_link.get("href"):
            return None

        detail_url = detail_link["href"]
        if detail_url.startswith("/"):
            detail_url = f"https://www.applyboard.com{detail_url}"

        return detail_url

    def scrape_program_detail_from_url(self, url: str) -> Dict[str, Any]:
        """
        Visit a program detail page and extract all data.

        Args:
            url: Program detail page URL

        Returns:
            Dictionary containing program data
        """
        program = {}

        # Wait a bit before loading the detail page (to avoid rate limiting)
        time.sleep(2)

        # Use existing driver instead of creating new one
        driver = self.driver
        if not driver:
            print(f"Failed to access driver for: {url}")
            return {}

        try:
            driver.get(url)
            # Wait for main content
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.MuiPaper-root")
                    )
                )
            except TimeoutException:
                print("⚠️ Timeout waiting for main content")
                return {}

            # Expand all sections
            self.expand_page_sections(driver)

            # Get page source for BeautifulSoup parsing
            detail_soup = BeautifulSoup(driver.page_source, "lxml")

            # Extract all required fields from detail page
            program.update(self.extract_program_detail(detail_soup))

            # Extract scholarships using Selenium (carousel navigation needed)
            scholarships = self.extract_scholarships(driver)
            program["scholarships"] = scholarships

            # Add program URL for reference
            program["program_url"] = url

        except Exception as e:
            print(f"Error scraping program detail: {e}")
            # Don't quit driver here - let scrape_programs_from_urls manage it

        return program

    def expand_page_sections(self, driver):
        """Expand all collapsible sections on the page."""
        # Click 'Show More' buttons
        try:
            show_more_buttons = driver.find_elements(
                By.XPATH, "//button[.//p[contains(text(),'Show More')]]"
            )
            print(f"   Found {len(show_more_buttons)} 'Show More' buttons...")

            clicked_count = 0
            for button in show_more_buttons:
                try:
                    if button.is_displayed():
                        driver.execute_script(
                            "arguments[0].scrollIntoView(true);", button
                        )
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", button)
                        clicked_count += 1
                        time.sleep(1)
                except Exception as e:
                    continue

            if clicked_count > 0:
                print(f"   ✓ Clicked {clicked_count} 'Show More' buttons")
        except Exception as e:
            print(f"   ⚠️  Error with Show More buttons: {e}")

        # Expand language test sections
        try:
            language_test_buttons = driver.find_elements(
                By.CSS_SELECTOR, "button[aria-expanded='false']"
            )
            print(f"   Found {len(language_test_buttons)} collapsed sections...")

            lang_expanded_count = 0
            for button in language_test_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", button)
                    lang_expanded_count += 1
                    time.sleep(0.5)
                except Exception as e:
                    continue

            if lang_expanded_count > 0:
                print(f"   ✓ Expanded {lang_expanded_count} collapsed sections")
                time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Error expanding sections: {e}")

        # Expand other accordions
        try:
            expand_buttons = driver.find_elements(
                By.CSS_SELECTOR, "button[aria-label='show more']"
            )
            print(f"   Found {len(expand_buttons)} sections to expand...")

            expanded_count = 0
            for button in expand_buttons:
                try:
                    is_expanded = button.get_attribute("aria-expanded")
                    if is_expanded == "false":
                        driver.execute_script(
                            "arguments[0].scrollIntoView(true);", button
                        )
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", button)
                        expanded_count += 1
                        time.sleep(0.5)
                except Exception as e:
                    continue

            if expanded_count > 0:
                print(f"   ✓ Expanded {expanded_count} more sections")
        except Exception as e:
            print(f"   ⚠️  Error expanding sections: {e}")

        time.sleep(2)

    def extract_scholarships(self, driver) -> List[Dict[str, Any]]:
        """
        Extract all scholarships from the carousel by clicking through them.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            List of scholarship dictionaries
        """
        scholarships = []

        try:
            # Find the scholarships section
            scholarships_section = driver.find_elements(
                By.CSS_SELECTOR, "section[aria-label='Scholarships']"
            )

            if not scholarships_section:
                print("   ℹ️  No scholarships section found")
                return scholarships

            print("   Found scholarships section, extracting...")

            # Scroll to scholarships section
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", scholarships_section[0]
            )
            time.sleep(1)

            # Track seen scholarship names to detect loop
            seen_scholarships = set()
            max_iterations = 20  # Safety limit
            iteration = 0

            while iteration < max_iterations:
                # Get current visible scholarship articles
                soup = BeautifulSoup(driver.page_source, "lxml")
                articles = soup.select('section[aria-label="Scholarships"] article')

                if not articles:
                    break

                # Extract data from visible scholarships
                new_scholarship_found = False

                for article in articles:
                    # Check if this article is visible (not aria-hidden="true")
                    parent_group = article.find_parent("div", attrs={"role": "group"})
                    if parent_group and parent_group.get("aria-hidden") == "true":
                        continue

                    scholarship = {}

                    # Extract scholarship name
                    name_elem = article.find(
                        "div", class_=lambda x: x and "css-1ts3v3l" in x if x else False
                    )
                    if name_elem:
                        scholarship["name"] = name_elem.get_text(strip=True)
                    else:
                        continue

                    # Skip if we've already seen this scholarship
                    if scholarship["name"] in seen_scholarships:
                        continue

                    new_scholarship_found = True
                    seen_scholarships.add(scholarship["name"])

                    # Extract university
                    uni_elem = article.find(
                        "div", class_=lambda x: x and "css-13llmdu" in x if x else False
                    )
                    if uni_elem:
                        scholarship["university"] = uni_elem.get_text(strip=True)

                    # Extract amount
                    amount_elem = article.find(
                        "div", class_=lambda x: x and "css-koraoo" in x if x else False
                    )
                    if amount_elem:
                        scholarship["amount"] = amount_elem.get_text(strip=True)

                    # Extract auto-applied status
                    auto_applied_containers = article.find_all(
                        "div", class_=lambda x: x and "css-1uqoi5f" in x if x else False
                    )
                    for container in auto_applied_containers:
                        label = container.find(
                            "div",
                            class_=lambda x: x and "css-f5mcgk" in x if x else False,
                        )
                        if label and "Auto applied" in label.get_text():
                            value = container.find_next_sibling(
                                "div",
                                class_=lambda x: (
                                    x and "css-1uqoi5f" in x if x else False
                                ),
                            )
                            if value:
                                value_div = value.find(
                                    "div",
                                    class_=lambda x: (
                                        x and "css-koraoo" in x if x else False
                                    ),
                                )
                                if value_div:
                                    scholarship["auto_applied"] = value_div.get_text(
                                        strip=True
                                    )
                            break

                    # Extract eligible nationalities
                    info_rows = article.find_all(
                        "div", class_=lambda x: x and "css-wpicwe" in x if x else False
                    )
                    for row in info_rows:
                        label_div = row.find(
                            "div",
                            class_=lambda x: x and "css-f5mcgk" in x if x else False,
                        )
                        if label_div:
                            label_text = label_div.get_text(strip=True)

                            if "Eligible nationalities" in label_text:
                                value_div = row.find(
                                    "div",
                                    class_=lambda x: (
                                        x and "css-a1smrc" in x if x else False
                                    ),
                                )
                                if value_div:
                                    scholarship["eligible_nationalities"] = (
                                        value_div.get_text(strip=True)
                                    )

                            elif "Eligible program levels" in label_text:
                                value_div = row.find(
                                    "div",
                                    class_=lambda x: (
                                        x and "css-a1smrc" in x if x else False
                                    ),
                                )
                                if value_div:
                                    scholarship["eligible_program_levels"] = (
                                        value_div.get_text(strip=True)
                                    )

                    # Extract "Learn more" URL
                    learn_more_link = article.find(
                        "a", class_=lambda x: x and "css-nxm9rc" in x if x else False
                    )
                    if learn_more_link:
                        href = learn_more_link.get("href", "")
                        if href:
                            if href.startswith("/"):
                                scholarship["learn_more_url"] = (
                                    f"https://www.applyboard.com{href}"
                                )
                            else:
                                scholarship["learn_more_url"] = href

                    scholarships.append(scholarship)
                    print(f"   ✓ Extracted scholarship: {scholarship['name']}")

                # If no new scholarships found, we've looped back
                if not new_scholarship_found:
                    print(
                        f"   ✓ Extracted all {len(scholarships)} scholarships (detected loop)"
                    )
                    break

                # Try to click the "Next" button
                try:
                    next_button = driver.find_element(
                        By.CSS_SELECTOR, "button[aria-label*='Next']"
                    )

                    # Check if button is enabled
                    if next_button.is_enabled():
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(1.5)  # Wait for carousel animation
                        iteration += 1
                    else:
                        print("   ℹ️  Next button disabled, reached end")
                        break

                except Exception as e:
                    print(f"   ℹ️  No more scholarships to navigate: {e}")
                    break

            if iteration >= max_iterations:
                print(f"   ⚠️  Reached max iterations ({max_iterations})")

        except Exception as e:
            print(f"   ⚠️  Error extracting scholarships: {e}")

        return scholarships

    def extract_program_detail(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract all required fields from the program detail page soup.
        """
        data = {}
        # Program Name
        program_name = ""
        # Look for the program name in the header section
        # The program name is in a <p> tag with specific styling
        program_name_tag = soup.find(
            "p",
            class_=lambda x: x and "MuiTypography-root" in x if x else False,
            attrs={"role": "heading"},
        )
        if program_name_tag:
            program_name = program_name_tag.get_text(strip=True)
        data["program_name"] = program_name
        # Program Summary
        summary = ""
        # Look for the section with "Program Summary" heading
        program_summary_heading = soup.find(
            "p", class_="MuiTypography-root", string="Program Summary"
        )
        if program_summary_heading:
            # Find the next MuiCard that contains the summary text
            summary_card = program_summary_heading.find_next(
                "div", class_="MuiCard-root"
            )
            if summary_card:
                # Find the container that holds all the content (including expanded content)
                # Look for the div with class containing "jss" that holds the actual content
                content_div = summary_card.find(
                    "div", class_=lambda x: x and "jss" in x if x else False
                )

                if content_div:
                    # Instead of manually parsing tags, get all meaningful text
                    # We'll extract text from specific elements to preserve structure
                    summary_parts = []

                    # Find the innermost div that contains the actual content (skip the outer wrapper)
                    actual_content = content_div.find("div")
                    if not actual_content:
                        actual_content = content_div

                    # Process all direct children and their text
                    def extract_text_recursive(element, parts_list):
                        """Recursively extract text while preserving structure"""
                        for child in element.children:
                            if child.name == "p":
                                # Get text from paragraph
                                text = child.get_text(" ", strip=True)
                                if text and text not in parts_list:
                                    parts_list.append(text)
                            elif child.name == "div":
                                # Check if this div has direct text (not in children)
                                direct_text = ""
                                for content in child.children:
                                    if isinstance(content, str):
                                        text_part = content.strip()
                                        if text_part:
                                            direct_text += text_part + " "
                                if (
                                    direct_text.strip()
                                    and direct_text.strip() not in parts_list
                                ):
                                    parts_list.append(direct_text.strip())
                                # Recurse into the div
                                extract_text_recursive(child, parts_list)
                            elif child.name == "ul":
                                # Process list
                                for li in child.find_all("li", recursive=False):
                                    text = li.get_text(" ", strip=True)
                                    if text and ("• " + text) not in parts_list:
                                        parts_list.append("• " + text)
                            elif child.name == "li":
                                # Individual list item
                                text = child.get_text(" ", strip=True)
                                if text and ("• " + text) not in parts_list:
                                    parts_list.append("• " + text)
                            elif isinstance(child, str):
                                # Direct text node
                                text = child.strip()
                                if text and text not in parts_list:
                                    parts_list.append(text)

                    extract_text_recursive(actual_content, summary_parts)
                    summary = " ".join(summary_parts)

                # Fallback: just get all text from the card
                if not summary:
                    summary = summary_card.get_text(" ", strip=True)

        # Alternative: try the old class name as fallback
        if not summary:
            about_div = soup.find("div", class_="cds-temp__aboutProgram")
            if about_div:
                p_tags = about_div.find_all("p")
                summary = " ".join(p.get_text(" ", strip=True) for p in p_tags)
        data["program_summary"] = summary

        # Program Info (Level, Length, Fees, etc.)
        info = {}

        # Look for the main program info card
        program_info_section = None
        for card in soup.find_all("div", class_="MuiCard-root"):
            # Check if this card contains program info containers
            if card.find(
                "div",
                {
                    "data-testid": lambda x: (
                        x and x.startswith("program-info-container-") if x else False
                    )
                },
            ):
                program_info_section = card
                break

        if program_info_section:
            # Extract main program info items
            info_containers = program_info_section.find_all(
                "div",
                {
                    "data-testid": lambda x: (
                        x and x.startswith("program-info-container-") if x else False
                    )
                },
            )

            for container in info_containers:
                # Get all paragraph tags in this container
                p_tags = container.find_all("p", class_="MuiTypography-root")
                if len(p_tags) >= 2:
                    # First p tag is the value, second is the label
                    value = p_tags[0].get_text(strip=True)
                    label = p_tags[1].get_text(strip=True)
                    info[label] = value

            # Now look for "Other Fees" or similar additional sections
            # Look for paragraphs with "Other Fees" text specifically
            other_fees_titles = program_info_section.find_all(
                "p",
                class_="MuiTypography-root",
                string=lambda x: x and "Other Fees" in x if x else False,
            )

            print(f"   Found {len(other_fees_titles)} 'Other Fees' sections")

            for other_fees_p in other_fees_titles:
                # Check if this is NOT inside a program-info-container
                parent_container = other_fees_p.find_parent(
                    "div",
                    {
                        "data-testid": lambda x: (
                            x and x.startswith("program-info-container-")
                            if x
                            else False
                        )
                    },
                )

                if not parent_container:
                    # This is a section title, not a value
                    section_title = other_fees_p.get_text(strip=True)
                    print(f"   Processing section: {section_title}")

                    # Find the parent container for this section
                    section_parent = other_fees_p.find_parent(
                        "div", class_=lambda x: x and "jss" in x if x else False
                    )

                    if section_parent:
                        fee_items = {}

                        # Look for all divs with spacing/grid classes that contain fee information
                        fee_containers = section_parent.find_all(
                            "div", class_=lambda x: x and "jss" in x if x else False
                        )

                        for fee_div in fee_containers:
                            # Find paragraphs within this div
                            paragraphs = fee_div.find_all(
                                "p", class_="MuiTypography-root", recursive=False
                            )

                            if len(paragraphs) >= 2:
                                # Try to identify label and value
                                # Look for the one with RZYf (label) and LblKF (value) or data-testid (value)
                                label = None
                                value = None

                                for p in paragraphs:
                                    p_classes = p.get("class", [])
                                    if "RZYf" in p_classes or "RZYf" in str(p_classes):
                                        label = p.get_text(strip=True)
                                    elif "LblKF" in p_classes or "LblKF" in str(
                                        p_classes
                                    ):
                                        value = p.get_text(" ", strip=True)
                                    elif p.get("data-testid"):
                                        # This is likely the value with more accurate formatting
                                        value = p.get_text(" ", strip=True)

                                # If we found both label and value, add them
                                if label and value and label != section_title:
                                    fee_items[label] = value

                        # Add the section if we found any fee items
                        if fee_items:
                            info[section_title] = fee_items

        # Fallback: try the old structure
        if not info:
            cost_and_duration_section = soup.find("h3", string="Cost and Duration")
            if cost_and_duration_section:
                section_div = cost_and_duration_section.find_parent("section")
                if section_div:
                    for item in section_div.find_all("div", class_="css-1pjzxzh"):
                        label_div = item.find("div", class_="css-1uo86s9")
                        value_div = item.find("div", class_="css-1a5xebh")
                        if label_div and value_div:
                            label = label_div.get_text(strip=True)
                            value = value_div.get_text(strip=True)
                            info[label] = value

        data["program_info"] = info

        # Program Intakes - Extract detailed information
        intakes = []
        intakes_section = soup.find("p", string="Program Intakes")
        if intakes_section:
            # Find all intake containers (each with status, month/year, and details)
            intake_containers = intakes_section.find_parent("div").find_all(
                "div",
                class_=lambda x: x and "css-19r1dcd" in x if x else False,
                recursive=False,
            )

            for container in intake_containers:
                intake_info = {}

                # Get status (Open/Likely open)
                status_chip = container.find("div", class_="MuiChip-root")
                if status_chip:
                    status_p = status_chip.find("p", class_="MuiTypography-root")
                    if status_p:
                        intake_info["status"] = status_p.get_text(strip=True)

                # Get month and year (e.g., "Mar 2026")
                month_year = container.find("p", attrs={"ml": "1"})
                if not month_year:
                    # Try alternative selector
                    month_year = container.find("p", class_="MuiTypography-root fHlKOe")
                if month_year:
                    intake_info["intake_date"] = month_year.get_text(strip=True)

                # Get open date and submission deadline from collapsed section
                collapse_section = container.find("div", class_="MuiCollapse-root")
                if collapse_section:
                    # Find all paragraphs in the collapse section
                    all_p_tags = collapse_section.find_all(
                        "p", class_="MuiTypography-root"
                    )

                    # Look for "Open date" and "Submission deadline" labels
                    i = 0
                    while i < len(all_p_tags):
                        text = all_p_tags[i].get_text(strip=True)

                        if "Open date" in text:
                            # The next p tag should contain the value
                            if i + 1 < len(all_p_tags):
                                next_text = all_p_tags[i + 1].get_text(strip=True)
                                # Skip if it's another label
                                if "Submission deadline" not in next_text:
                                    intake_info["open_date"] = next_text
                                    i += 1  # Skip the value tag
                        elif "Submission deadline" in text:
                            # The next p tag should contain the value
                            if i + 1 < len(all_p_tags):
                                next_text = all_p_tags[i + 1].get_text(strip=True)
                                # Make sure it's not another label
                                if not any(
                                    keyword in next_text
                                    for keyword in ["Open date", "Submission"]
                                ):
                                    intake_info["submission_deadline"] = next_text
                                    i += 1  # Skip the value tag

                        i += 1

                # Only add if we got some data
                if intake_info:
                    intakes.append(intake_info)

        data["program_intakes"] = intakes

        # Residence Permit for Job Seekers
        permit = ""
        permit_section = soup.find(
            "div", class_="css-ubjcg", string="Residence Permit for Job Seekers"
        )
        if permit_section:
            details = permit_section.find_parent(
                "div", class_="MuiAccordionSummary-content"
            )
            if details:
                permit_detail = details.find_next(
                    "div", class_="MuiAccordionDetails-root"
                )
                if permit_detail:
                    permit = permit_detail.get_text(" ", strip=True)
        data["residence_permit"] = permit

        # Admission Requirements
        requirements = {}
        req_section = soup.find("p", string="Admission Requirements")
        if req_section:
            # Get the main container - find the parent that contains all requirements
            main_container = req_section.find_parent("div", class_="MuiBox-root")

            # Look for the container with jss106 class or find the one that has Academic Background
            # Go up a few levels to get the right container
            for _ in range(5):  # Try up to 5 parent levels
                if main_container and main_container.find(
                    "p",
                    string=lambda x: x and "Academic Background" in x if x else False,
                ):
                    break
                if main_container:
                    main_container = main_container.find_parent(
                        "div", class_="MuiBox-root"
                    )
                else:
                    break

            if main_container:
                # Extract Academic Background
                academic_bg = {}

                # Find "Academic Background" section
                academic_section = main_container.find(
                    "p",
                    string=lambda x: x and "Academic Background" in x if x else False,
                )
                if academic_section:
                    # Find the parent container that holds all academic requirements
                    academic_container = academic_section.find_next(
                        "div", class_="MuiBox-root"
                    )

                    if academic_container:
                        # Find Minimum Level of Education
                        min_edu_label = academic_container.find(
                            "p", string="Minimum Level of Education Completed"
                        )
                        if min_edu_label:
                            # Look for the collapse section that contains the value
                            collapse = min_edu_label.find_parent("div").find_next(
                                "div", class_="MuiCollapse-root"
                            )
                            if collapse:
                                edu_value = collapse.find(
                                    "p", class_="MuiTypography-root"
                                )
                                if edu_value:
                                    academic_bg["minimum_education"] = (
                                        edu_value.get_text(strip=True)
                                    )

                        # Find Minimum GPA
                        min_gpa_label = academic_container.find(
                            "p", string="Minimum GPA"
                        )
                        if min_gpa_label:
                            # Look for the collapse section
                            collapse = min_gpa_label.find_parent("div").find_next(
                                "div", class_="MuiCollapse-root"
                            )
                            if collapse:
                                gpa_value = collapse.find(
                                    "p", class_="MuiTypography-root"
                                )
                                if gpa_value:
                                    academic_bg["minimum_gpa"] = gpa_value.get_text(
                                        strip=True
                                    )

                requirements["academic_background"] = academic_bg

                # Extract Language Test Scores - DYNAMIC extraction for all tests
                language_tests = {}

                # Find "Minimum Language Test Scores" section
                lang_section = main_container.find(
                    "p", string="Minimum Language Test Scores"
                )
                if lang_section:
                    print("   Found 'Minimum Language Test Scores' section")
                    # Find the container that holds all language tests
                    lang_container = lang_section.find_next("div", class_="MuiBox-root")

                    if lang_container:
                        # Find ALL language test containers dynamically
                        # Look for divs with the specific class pattern that contains test names
                        test_containers = lang_container.find_all(
                            "div",
                            class_=lambda x: x and "css-19x5vgl" in x if x else False,
                        )

                        print(
                            f"   Found {len(test_containers)} language test containers"
                        )

                        for test_container in test_containers:
                            # Find the test name (e.g., "IELTS", "TOEFL", "PTE", "DUOLINGO")
                            # Look for the first MuiBox-root that contains the test label
                            label_box = test_container.find(
                                "div", class_="MuiBox-root", recursive=False
                            )

                            if label_box:
                                test_label_p = label_box.find(
                                    "p", class_="MuiTypography-root"
                                )

                                if test_label_p:
                                    test_name = test_label_p.get_text(strip=True)

                                    # Skip if it's not a test name
                                    if not test_name or test_name in [
                                        "Show More",
                                        "Show Less",
                                    ]:
                                        continue

                                    print(f"   Processing language test: {test_name}")

                                    # Find the collapse section with the test score
                                    # Look for MuiCollapse-root that should now be expanded
                                    collapse = test_container.find(
                                        "div",
                                        class_=lambda x: (
                                            x and "MuiCollapse-root" in x
                                            if x
                                            else False
                                        ),
                                    )

                                    if collapse:
                                        # Check if collapse is entered (expanded)
                                        # The content should be in MuiCollapse-wrapper
                                        wrapper = collapse.find(
                                            "div", class_="MuiCollapse-wrapper"
                                        )
                                        if wrapper:
                                            # Find the wrapperInner which contains the actual content
                                            inner = wrapper.find(
                                                "div", class_="MuiCollapse-wrapperInner"
                                            )
                                            if inner:
                                                # Find all paragraphs in the inner section
                                                all_paragraphs = inner.find_all(
                                                    "p", class_="MuiTypography-root"
                                                )

                                                # The score should be in one of these paragraphs
                                                # Look for the one with class containing "fPdfYJ" or similar
                                                test_value = None
                                                for p in all_paragraphs:
                                                    text = p.get_text(strip=True)
                                                    # Skip empty or non-score text
                                                    if text and text not in ["", " "]:
                                                        test_value = p
                                                        break

                                                if test_value:
                                                    value_text = test_value.get_text(
                                                        strip=True
                                                    )
                                                    print(
                                                        f"   ✓ Extracted {test_name}: {value_text}"
                                                    )

                                                    # Check if this test has detailed sub-scores
                                                    # Extract ALL subscores dynamically (don't rely on specific names)
                                                    detail_boxes = inner.find_all(
                                                        "div", class_="MuiBox-root"
                                                    )

                                                    subscores = {}
                                                    for box in detail_boxes:
                                                        all_p = box.find_all(
                                                            "p",
                                                            class_="MuiTypography-root",
                                                        )
                                                        if len(all_p) >= 2:
                                                            label = all_p[0].get_text(
                                                                strip=True
                                                            )
                                                            value = all_p[1].get_text(
                                                                strip=True
                                                            )

                                                            # Filter out non-subscore elements
                                                            # Skip if label is empty, or matches known non-score text
                                                            skip_labels = [
                                                                "Show More",
                                                                "Show Less",
                                                                "",
                                                                " ",
                                                                test_name,  # Don't add test name itself
                                                            ]

                                                            # Skip if value doesn't look like a score
                                                            # (should have numbers, not be too long)
                                                            if (
                                                                label
                                                                and value
                                                                and label
                                                                not in skip_labels
                                                                and len(value)
                                                                < 20  # Scores are short
                                                                and not label.startswith(
                                                                    "Minimum"
                                                                )
                                                                and not label.startswith(
                                                                    "This program"
                                                                )
                                                            ):
                                                                # Check if value looks numeric or score-like
                                                                # (contains digits or common score patterns)
                                                                if any(
                                                                    char.isdigit()
                                                                    for char in value
                                                                ):
                                                                    subscores[
                                                                        label.lower()
                                                                    ] = value
                                                                    print(
                                                                        f"   ✓ {test_name} - {label}: {value}"
                                                                    )

                                                    # If we found subscores, store as dict with overall + subscores
                                                    # Otherwise, just store the overall score as a string
                                                    if subscores:
                                                        test_data = {
                                                            "overall": value_text,
                                                            **subscores,  # Merge all subscores
                                                        }
                                                        language_tests[test_name] = (
                                                            test_data
                                                        )
                                                    else:
                                                        # No subscores found, just store overall score
                                                        language_tests[test_name] = (
                                                            value_text
                                                        )
                                                else:
                                                    print(
                                                        f"   ⚠️  Could not find test value for {test_name}"
                                                    )
                                            else:
                                                print(
                                                    f"   ⚠️  Could not find wrapperInner for {test_name}"
                                                )
                                        else:
                                            print(
                                                f"   ⚠️  Could not find wrapper for {test_name}"
                                            )
                                    else:
                                        print(
                                            f"   ⚠️  Could not find collapse section for {test_name}"
                                        )
                else:
                    print("   ⚠️  'Minimum Language Test Scores' section not found")

                requirements["language_tests"] = language_tests

                # Extract additional requirements (valid test results, nationality-specific)
                additional_reqs = []

                # Check for "requires valid language test results"
                valid_test_label = main_container.find(
                    "p", string="This program requires valid language test results"
                )
                if valid_test_label:
                    # Find the parent container and then the collapse section
                    parent_div = valid_test_label.find_parent("div")
                    if parent_div:
                        collapse = parent_div.find_next(
                            "div", class_="MuiCollapse-root"
                        )
                        if collapse:
                            # Look for the actual text content
                            test_req_text = collapse.find(
                                "p", attrs={"data-testid": "allows-for-all-countries"}
                            )
                            if test_req_text:
                                additional_reqs.append(
                                    {
                                        "type": "valid_test_results",
                                        "description": test_req_text.get_text(
                                            strip=True
                                        ),
                                    }
                                )

                # Check for nationality-specific English requirements
                nationality_label = main_container.find(
                    "p",
                    string="This program has nationality specific English requirements",
                )
                if nationality_label:
                    # Find the parent container
                    parent_div = nationality_label.find_parent("div")
                    if parent_div:
                        collapse = parent_div.find_next(
                            "div", class_="MuiCollapse-root"
                        )
                        if collapse:
                            # Find the nationality-specific data
                            nationality_data = {}

                            # Look for the program-ere-info div
                            ere_info = collapse.find(
                                "div", attrs={"data-testid": "program-ere-info"}
                            )
                            if ere_info:
                                # Find all accordion sections (one per country)
                                accordions = ere_info.find_all(
                                    "div", class_="MuiAccordion-root"
                                )

                                for accordion in accordions:
                                    # Get country name from accordion summary
                                    summary = accordion.find(
                                        "div", class_="MuiAccordionSummary-content"
                                    )
                                    if summary:
                                        country = summary.get_text(strip=True)

                                        # Get the table with test scores
                                        table = accordion.find(
                                            "table", class_="MuiTable-root"
                                        )
                                        if table:
                                            country_reqs = []
                                            tbody = table.find("tbody")
                                            if tbody:
                                                rows = tbody.find_all("tr")
                                                for row in rows:
                                                    cells = row.find_all(["th", "td"])
                                                    if len(cells) >= 6:
                                                        test_name = cells[0].get_text(
                                                            strip=True
                                                        )
                                                        test_data = {
                                                            "test": test_name,
                                                            "L": cells[1].get_text(
                                                                strip=True
                                                            ),
                                                            "R": cells[2].get_text(
                                                                strip=True
                                                            ),
                                                            "S": cells[3].get_text(
                                                                strip=True
                                                            ),
                                                            "W": cells[4].get_text(
                                                                strip=True
                                                            ),
                                                            "O": cells[5].get_text(
                                                                strip=True
                                                            ),
                                                        }
                                                        country_reqs.append(test_data)

                                            if country_reqs:
                                                nationality_data[country] = country_reqs

                            if nationality_data:
                                additional_reqs.append(
                                    {
                                        "type": "nationality_specific",
                                        "data": nationality_data,
                                    }
                                )

                # Check for "conditional admissions" requirements
                conditional_label = main_container.find(
                    "p",
                    string="This program offers conditional admissions",
                )
                if conditional_label:
                    # Find the parent container
                    parent_div = conditional_label.find_parent("div")
                    if parent_div:
                        collapse = parent_div.find_next(
                            "div", class_="MuiCollapse-root"
                        )
                        if collapse:
                            # Look for the conditional admission text
                            conditional_text_elem = collapse.find(
                                "span",
                                attrs={
                                    "data-testid": "conditional-admission-require-elp"
                                },
                            )
                            if conditional_text_elem:
                                # Get the full text including list items
                                conditional_text = conditional_text_elem.get_text(
                                    " ", strip=True
                                )

                                # Also try to extract structured data from list items
                                conditional_details = []
                                list_items = conditional_text_elem.find_all(
                                    "li", attrs={"data-testid": True}
                                )

                                for li in list_items:
                                    testid = li.get("data-testid", "")
                                    text = li.get_text(strip=True)
                                    conditional_details.append(
                                        {"test_type": testid, "requirement": text}
                                    )

                                additional_reqs.append(
                                    {
                                        "type": "conditional_admission",
                                        "description": conditional_text,
                                        "details": (
                                            conditional_details
                                            if conditional_details
                                            else None
                                        ),
                                    }
                                )

                requirements["additional_requirements"] = additional_reqs

                # Extract disclaimer
                disclaimer = main_container.find(
                    "p", string=lambda x: x and "do not guarantee admission" in x
                )
                if disclaimer:
                    requirements["disclaimer"] = disclaimer.get_text(strip=True)

        data["admission_requirements"] = requirements

        # University Info
        uni_info = {}
        uni_link = soup.find("a", class_="css-vzjlnl")
        if uni_link:
            uni_info["university_name"] = uni_link.get_text(strip=True)
            uni_info["university_url"] = "https://www.applyboard.com" + uni_link.get(
                "href", ""
            )
            location = uni_link.find_next("p", class_="MuiTypography-root")
            if location:
                uni_info["location"] = location.get_text(strip=True)
        data["university_info"] = uni_info

        # Program ID / Views count
        program_id = soup.find("p", class_="MuiTypography-root sc-eCYdqJ dveSWF")
        if program_id:
            data["program_id"] = program_id.get_text(strip=True)

        # Extract program features/tags dynamically (Scholarships, Fast Acceptance, etc.)
        program_features = []

        # Look for the container with the features
        # The HTML structure has a div.css-ivaslv that contains buttons with features
        features_container = soup.find("div", class_="css-ivaslv")
        if features_container:
            # Find all buttons that contain feature information
            feature_buttons = features_container.find_all(
                "button", class_="css-1y8tkjk"
            )

            for button in feature_buttons:
                # Each button has a span with class css-1wftnvw containing the feature text
                feature_span = button.find("span", class_="css-1wftnvw")
                if feature_span:
                    feature_text = feature_span.get_text(strip=True)
                    if feature_text:  # Only add non-empty features
                        program_features.append(feature_text)

        data["program_features"] = program_features

        # Extract Scholarships - this needs to be done with Selenium for carousel navigation
        # We'll add a placeholder here and extract it in the scraping function
        data["scholarships"] = []

        return data

    def collect_program_urls(
        self, programs_url: str, max_items: int = None
    ) -> List[str]:
        """
        Collect program URLs from the listing pages (without visiting detail pages).

        Args:
            programs_url: URL of the programs page
            max_items: Maximum number of URLs to collect (None to ask user)

        Returns:
            List of program URLs
        """
        print(f"\n🔍 Collecting program URLs from: {programs_url}")

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

        print(f"🎯 Will collect {max_items} program URLs")
        print("=" * 50 + "\n")

        all_urls = []
        page_num = 1

        while len(all_urls) < max_items:
            print(f"📄 Collecting URLs from page {page_num}...")

            # Parse current page - use more flexible selector
            # Find all article elements with aria-label attribute (more robust)
            articles = soup.find_all("article", attrs={"aria-label": True})

            # Fallback to class-based search if no articles found
            if not articles:
                articles = soup.find_all(
                    "article", class_=lambda x: x and "css-" in x if x else False
                )

            print(f"   Found {len(articles)} program cards on this page")

            for article in articles:
                if len(all_urls) >= max_items:
                    break

                url = self.extract_program_url_from_card(article)
                if url:
                    all_urls.append(url)
                    print(f"   ✓ Collected URL #{len(all_urls)}")

            # Check if we need to fetch next page
            if len(all_urls) >= max_items or len(all_urls) >= total_items:
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

        print(f"\n✅ Total program URLs collected: {len(all_urls)}")
        return all_urls

    def scrape_programs_from_urls(
        self, program_urls: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape detailed program data by visiting each program URL.

        Args:
            program_urls: List of program detail page URLs

        Returns:
            List of program data dictionaries
        """
        print(f"\n📚 Starting detailed scraping of {len(program_urls)} programs...")
        print("=" * 50 + "\n")

        all_programs = []

        # Ensure driver is set up once before scraping all programs
        if not self.driver:
            self.setup_driver()

        for idx, url in enumerate(program_urls, 1):
            print(f"📖 Scraping program {idx}/{len(program_urls)}...")
            print(f"   URL: {url}")

            try:
                program = self.scrape_program_detail_from_url(url)
                if program and program.get("program_name"):  # Verify we got actual data
                    all_programs.append(program)
                    # Show a preview of what was scraped
                    program_name = program.get("university_info", {}).get(
                        "university_name", "Unknown"
                    )
                    print(f"   ✓ Scraped: {program_name}")
                else:
                    print(f"   ✗ Failed to scrape this program (no data returned)")
            except Exception as e:
                print(f"   ✗ Exception while scraping: {e}")
                # If driver crashed, try to recover
                if (
                    "invalid session id" in str(e).lower()
                    or "connection" in str(e).lower()
                ):
                    print("   🔧 Driver issue detected, restarting driver...")
                    self.close_driver()
                    self.setup_driver()

            # Show progress
            print(
                f"   Progress: {len(all_programs)}/{len(program_urls)} programs completed\n"
            )

        print(
            f"\n✅ Total programs successfully scraped: {len(all_programs)}/{len(program_urls)}"
        )
        return all_programs


# Example usage
if __name__ == "__main__":
    # Create ApplyBoard scraper
    scraper = ApplyBoardScraper()

    # Step 1: Get study destinations
    countries = scraper.get_study_destinations()

    if not countries:
        print("❌ Could not fetch study destinations")
        scraper.close_driver()
        exit(1)

    # Step 2: Display menu and get user selection
    selected_country, country_url = scraper.display_country_menu()

    if not country_url:
        print("No country selected. Exiting...")
        scraper.close_driver()
        exit(0)

    # Step 3: Get the "Explore more programs" link
    programs_url = scraper.get_explore_programs_link(country_url)

    if not programs_url:
        print("❌ Could not find programs link")
        scraper.close_driver()
        exit(1)

    # Step 4: Collect all program URLs (fast, without logging in)
    program_urls = scraper.collect_program_urls(programs_url)

    if not program_urls:
        print("\n❌ No program URLs were collected")
        scraper.close_driver()
        exit(1)

    # Step 5: Login (automatically using .env credentials)
    print("\n" + "=" * 50)
    print("🔐 APPLYBOARD LOGIN")
    print("=" * 50)
    print("ℹ️  Attempting to login using credentials from .env file...")

    if not scraper.login():
        print("\n❌ Login failed. Continuing without authentication...")
        print("Note: Some features may be limited without login.\n")
        time.sleep(2)
    else:
        print("✅ Successfully logged in!\n")
        time.sleep(1)

    # Step 6: Scrape detailed data from each program URL
    programs = scraper.scrape_programs_from_urls(program_urls)

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
