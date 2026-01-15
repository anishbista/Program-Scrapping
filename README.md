# ApplyBoard Web Scraper

A Python-based web scraping tool that extracts study abroad program data from ApplyBoard.com and stores it in JSON format.

## 🚀 Features

- ✅ **Interactive Country Selection** - Choose from 6 study destinations
- ✅ **Flexible Data Collection** - Scrape specific number of programs or all available
- ✅ **Automatic Pagination** - Handles multiple pages automatically (48 items per page)
- ✅ **Comprehensive Data** - Extracts 15+ data points per program
- ✅ **JSON Export** - Clean, structured output with metadata
- ✅ **Progress Tracking** - Real-time updates during scraping
- ✅ **Error Handling** - Graceful handling of network issues

## 📋 Prerequisites

- Python 3.7+
- Virtual environment (venv)
- Internet connection

## 🔧 Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

Simply run:
```bash
python scraper.py
```

The scraper will guide you through:
1. Selecting a study destination country
2. Choosing how many programs to scrape
3. Automatic data extraction and JSON export

For detailed usage instructions, see [USAGE.md](USAGE.md)

## 📊 Data Collected

Each program includes:
- School name and URL
- Program name and URL
- Degree type
- Location and campus city
- Tuition fees
- Application fee
- Program duration
- Success chance rating
- Available intake dates
- Special features (scholarships, fast acceptance, etc.)

## 📁 Output

Data is saved as JSON files with naming pattern:
```
{country}_programs_{timestamp}.json
```

Example: `germany_programs_20260115_143052.json`

## 🌍 Supported Countries

- Australia
- Canada
- Ireland
- Germany
- United Kingdom
- United States

## 📦 Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser

## 💡 Example

```bash
$ python scraper.py

# Select country: Germany
# Total available: 830 programs
# Scrape: 50 programs
# Output: germany_programs_20260115_143052.json
```

## ⚙️ Technical Details

- Automatically switches to 48 items per page for efficiency
- Handles multi-page scraping automatically
- Robust error handling for network issues
- Clean, modular code architecture

## 📝 Notes

- Scraping large datasets (500+ programs) may take several minutes
- The scraper respects timeouts to avoid overloading the server
- All data is scraped from publicly available pages

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the scraper.

## 📄 License

This project is for educational purposes.
