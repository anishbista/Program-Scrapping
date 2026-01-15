# Web Scraper Project

A Python-based web scraping tool that extracts data from websites and stores it in JSON format.

## Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Edit `scraper.py` and replace the URL with your target website:

```python
scraper = WebScraper("https://your-target-site.com")
scraper.run()
```

Run the scraper:
```bash
python scraper.py
```

### Custom Scraping

For custom scraping logic, modify the `scrape_data()` method or create custom extraction:

```python
from scraper import WebScraper

# Initialize scraper
scraper = WebScraper("https://example.com")

# Fetch page
soup = scraper.fetch_page()

# Custom extraction
if soup:
    data = []
    
    # Find elements using CSS selectors or find methods
    items = soup.select('.your-selector')
    
    for item in items:
        data_item = {
            'field1': item.select_one('.class-name').get_text(strip=True),
            'field2': item.find('tag')['attribute'],
            # Add more fields as needed
        }
        data.append(data_item)
    
    # Save to JSON
    scraper.save_to_json(data, 'output.json')
```

## Output Format

The scraper saves data in JSON format with metadata:

```json
{
  "scraped_at": "2026-01-15T12:00:00",
  "source_url": "https://example.com",
  "total_items": 10,
  "data": [
    {
      "title": "Item 1",
      "link": "https://example.com/item1",
      "description": "Description here"
    }
  ]
}
```

## Tips

1. **Finding Selectors:**
   - Right-click element in browser → Inspect
   - Use browser DevTools to find CSS selectors
   - Common selectors: `.class`, `#id`, `tag`, `[attribute]`

2. **Respectful Scraping:**
   - Check the website's `robots.txt`
   - Add delays between requests if scraping multiple pages
   - Respect rate limits

3. **Error Handling:**
   - The scraper includes timeout and error handling
   - Check console output for error messages

## Common Selectors

- `soup.find('tag')` - Find first tag
- `soup.find_all('tag')` - Find all tags
- `soup.select('.class')` - CSS selector
- `soup.select_one('#id')` - Single element by ID
- `element.get_text(strip=True)` - Get text content
- `element['attribute']` - Get attribute value

## Examples

See `examples/` folder for specific scraping examples (to be added).
