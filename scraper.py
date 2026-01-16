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
        self.is_logged_in = False

    def setup_driver(self):
        """Setup Selenium WebDriver (tries Firefox first, then Chrome)."""
        if self.driver:
            return self.driver

        try:
            print("🔧 Setting up Firefox WebDriver...")
            options = FirefoxOptions()
            options.add_argument("--headless")  # Run in background
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
                options.add_argument("--headless")
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
        Log in to ApplyBoard using provided credentials.

        Args:
            email: User's email (will prompt if not provided)
            password: User's password (will prompt if not provided)

        Returns:
            True if login successful, False otherwise
        """
        driver = self.setup_driver()
        if not driver:
            return False

        if not email:
            email = input("📧 Enter your ApplyBoard email: ").strip()
        if not password:
            import getpass

            password = getpass.getpass("🔒 Enter your password: ").strip()

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
        Extract data from a single program card by visiting its detail page.
        """
        program = {}

        # Find the div with class 'css-0' and then the <a> inside it
        div = article.find("div", class_="css-0")
        detail_link = None
        if div:
            detail_link = div.find("a", class_="css-cxyr4a", href=True)
        if not detail_link or not detail_link["href"]:
            print("No detail link found in card.")
            return {}

        detail_url = detail_link["href"]
        if detail_url.startswith("/"):
            detail_url = f"https://www.applyboard.com{detail_url}"
        # Wait a bit before loading the detail page (to avoid rate limiting and ensure load)
        time.sleep(2)

        # Visit detail page with Selenium
        detail_soup = self.fetch_detail_page_with_js(detail_url)
        if not detail_soup:
            print(f"Failed to load detail page: {detail_url}")
            return {}
        # Extract all required fields from detail page
        program.update(self.extract_program_detail(detail_soup))

        # Add program URL for reference
        program["program_url"] = detail_url

        return program

    def fetch_detail_page_with_js(self, url: str) -> BeautifulSoup:
        driver = self.setup_driver()
        if not driver:
            return None

        try:
            driver.get(url)
            # Try to wait for a unique element that always appears on the detail page
            try:
                # WebDriverWait(driver, 20).until(
                #     EC.presence_of_element_located(
                #         (By.CSS_SELECTOR, "div.MuiPaper-root")
                #     )
                # )
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.MuiPaper-root")
                    )
                )
            except TimeoutException:
                print("⚠️ Timeout waiting for main content, continuing anyway...")

            # Click 'Show More' for program summary if present
            try:
                show_more_btn = driver.find_element(
                    By.XPATH, "//button[.//p[contains(text(),'Show More')]]"
                )
                if show_more_btn.is_displayed():
                    driver.execute_script("arguments[0].click();", show_more_btn)
                    time.sleep(2)
            except Exception:
                pass  # No show more button

            # Wait for dynamic content to expand
            time.sleep(2)
            return BeautifulSoup(driver.page_source, "lxml")
        except Exception as e:
            print(f"Error loading detail page: {e}")
            return None

    def extract_program_detail(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract all required fields from the program detail page soup.
        """
        data = {}

        # Program Summary
        summary = ""
        about_div = soup.find("div", class_="cds-temp__aboutProgram")
        if about_div:
            p_tags = about_div.find_all("p")
            summary = " ".join(p.get_text(" ", strip=True) for p in p_tags)
        data["program_summary"] = summary

        # Program Info (Level, Length, Fees, etc.)
        info = {}
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

        # Program Intakes
        intakes = []
        intakes_section = soup.find("p", string="Program Intakes")
        if intakes_section:
            intakes_box = intakes_section.find_parent("div")
            if intakes_box:
                for intake_div in intakes_box.find_all(
                    "div", class_="MuiBox-root", recursive=True
                ):
                    date_p = intake_div.find(
                        "p",
                        class_="MuiTypography-root",
                        style=lambda x: x and "overflow" in x,
                    )
                    if date_p:
                        intakes.append(date_p.get_text(strip=True))
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
            req_box = req_section.find_parent("div")
            if req_box:
                for p in req_box.find_all("p", class_="MuiTypography-root"):
                    label = p.get_text(strip=True)
                    next_div = p.find_next_sibling("div")
                    if next_div:
                        value = next_div.get_text(" ", strip=True)
                        requirements[label] = value
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

        # Other Details (views, fast acceptance, etc.)
        fast_accept = soup.find("span", class_="css-1wftnvw")
        if fast_accept:
            data["fast_acceptance"] = fast_accept.get_text(strip=True)
        views = soup.find(
            "p", class_="MuiTypography-root", style=lambda x: x and "color" in x
        )
        if views:
            data["views"] = views.get_text(strip=True)

        return data

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
    # Step 0: Login
    print("=" * 50)
    print("🔐 APPLYBOARD LOGIN")
    print("=" * 50)

    login_choice = input("\nDo you want to login? (y/n): ").strip().lower()

    if login_choice == "y":
        if not scraper.login():
            print("\n❌ Login failed. Continuing without authentication...")
            print("Note: Some features may be limited without login.\n")
            time.sleep(2)
    else:
        print("\n⚠️  Continuing without login. Some features may be limited.\n")
        time.sleep(1)

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
