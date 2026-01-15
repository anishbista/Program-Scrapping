#!/usr/bin/env python3
"""
Test script to verify Selenium can load ApplyBoard programs page correctly
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import time


def test_selenium():
    """Test Selenium with ApplyBoard"""

    print("🧪 Testing Selenium setup...\n")

    # Try Firefox first
    driver = None
    try:
        print("🔧 Trying Firefox...")
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        print("✓ Firefox WebDriver initialized")
    except Exception as e:
        print(f"❌ Firefox failed: {e}\n")
        try:
            print("🔧 Trying Chrome...")
            options = ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            print("✓ Chrome WebDriver initialized")
        except Exception as e2:
            print(f"❌ Chrome also failed: {e2}")
            print(
                "\n⚠️  Please install Firefox or Chrome and the corresponding WebDriver"
            )
            return False

    if not driver:
        return False

    # Test URL (Germany programs)
    url = "https://www.applyboard.com/search?filter%5Blocations%5D=de&page%5Bsize%5D=48"

    try:
        print(f"\n🌐 Loading: {url}")
        driver.get(url)

        print("⏳ Waiting for content to load (10 seconds)...")
        time.sleep(10)  # Wait for JavaScript to execute

        # Get page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")

        # Find articles
        articles = soup.find_all("article", class_="css-1v3njm")
        print(f"\n✅ Found {len(articles)} program articles!")

        if articles:
            print("\n📝 First program:")
            first_program = articles[0]
            program_name = first_program.find("h2", class_="css-7iklpx")
            school_name = first_program.find("h3", class_="css-1a91344")

            if program_name:
                print(f"   Program: {program_name.get_text(strip=True)}")
            if school_name:
                print(f"   School: {school_name.get_text(strip=True)}")

            print("\n✅ Selenium is working correctly!")
            return True
        else:
            print("\n⚠️  No articles found. The page might need more time to load.")
            print("Let me save the HTML to inspect...")
            with open("test_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print("💾 Saved to test_page.html")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        driver.quit()
        print("\n🔒 Browser closed")


if __name__ == "__main__":
    success = test_selenium()
    if success:
        print("\n🎉 All tests passed! The scraper should work now.")
    else:
        print("\n💡 Tip: Make sure Firefox or Chrome is installed on your system.")
