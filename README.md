# ApplyBoard Web Scraper 🎓

A **high-performance** Python web scraper that extracts comprehensive study abroad program data from ApplyBoard.com with advanced features like batch saving, resume capability, and CSV export.

## 🚀 Key Features

### Core Functionality
- ✅ **Two Scraping Modes** - Extract from URL list or discover programs by country
- ✅ **URL JSON Import** - Provide pre-collected program URLs via JSON file
- ✅ **Interactive Country Selection** - Choose from 6+ study destinations
- ✅ **Flexible Data Collection** - Scrape specific number of programs or all available
- ✅ **Automatic Pagination** - Handles multiple pages automatically (48 items per page)
- ✅ **Comprehensive Data** - Extracts 20+ data points per program
- ✅ **Multiple Export Formats** - JSON and CSV output

### 🔥 Performance Optimizations
- ⚡ **Headless Browser Mode** - 2-3x faster scraping
- 💾 **Batch Saving** - Auto-saves every 50 programs (prevents data loss)
- 🔄 **Resume Capability** - Continue interrupted scrapes from where you left off
- 🧹 **Memory Management** - Periodic cache clearing for long-running scrapes
- 📊 **Progress Tracking** - Real-time updates with detailed statistics
- 🛡️ **Error Recovery** - Automatic driver restart on connection issues

## 📋 Prerequisites

- **Python 3.7+** (Tested on Python 3.13)
- **Firefox or Chrome browser** (with corresponding WebDriver)
- **Internet connection**
- **ApplyBoard account** (for detailed program data)

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**Required packages:**
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.15.0
python-dotenv>=1.0.0
```

### 2. Install WebDriver

**For Firefox (Recommended):**
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install firefox-geckodriver

# macOS
brew install geckodriver

# Or download from: https://github.com/mozilla/geckodriver/releases
```

**For Chrome:**
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

### 3. Configure Credentials

Create a `.env` file in the project directory:

```bash
# Create .env file
touch .env
```

Add your ApplyBoard credentials:
```env
APPLYBOARD_EMAIL=your_email@example.com
APPLYBOARD_PASSWORD=your_password
```

**⚠️ Important:** Never commit the `.env` file to version control!

## 🎯 How to Run

### Basic Usage

```bash
python scraper.py
```

The scraper will present two options:

#### **Option 1: Extract from URL JSON File**
Use this when you already have a list of program URLs to scrape.

1. **Prepare URL file** - Edit `url.json` with your program URLs:
   ```json
   {
     "urls": [
       "https://www.applyboard.com/programs/program-1",
       "https://www.applyboard.com/programs/program-2",
       "https://www.applyboard.com/programs/program-3"
     ]
   }
   ```

2. **Run scraper** - Select option `1`

3. **Specify quantity** - Choose how many programs to extract:
   ```
   How many programs to extract (1-50, or 'all'): 10
   ```

4. **Automatic Login** - Scraper logs in using `.env` credentials

5. **Data Extraction** - Scrapes specified number of programs

6. **Output Files**:
   - `programs_from_json_{timestamp}.json` - Complete dataset
   - `programs_from_json_{timestamp}_urls.json` - URL list with metadata

#### **Option 2: Discover and Extract by Country**
Use this to automatically discover programs from a specific country.

1. **Run scraper** - Select option `2`

2. **Select Country** - Choose from available study destinations:
   ```
   1. Australia
   2. Canada
   3. Germany
   4. Ireland
   5. United Kingdom
   6. United States
   ```

3. **Automatic Discovery** - Scraper collects all program URLs from selected country

4. **Automatic Login** - Scraper logs in using `.env` credentials

5. **Data Collection** - Scraper extracts data with:
   - Real-time progress updates
   - Batch saving every 50 programs
   - Automatic error recovery

6. **Output Files**:
   - `{country}_programs_{timestamp}.json` - Complete dataset
   - `{country}_programs_{timestamp}_urls.json` - URL list with metadata
   - `{country}_batch_N_{timestamp}.json` - Incremental backups
   - `{country}_progress.json` - Resume checkpoint (auto-deleted on success)

### Quick Examples

**Example 1: Extract 10 programs from URL list**
```bash
$ python scraper.py
Choose an option:
1. Extract programs from URL JSON file (url.json)
2. Discover and extract programs from countries
Enter your choice (1 or 2): 1

How many programs to extract (1-50, or 'all'): 10
# Output: programs_from_json_20260129_143052.json
```

**Example 2: Extract all programs from Germany**
```bash
$ python scraper.py
Choose an option:
1. Extract programs from URL JSON file (url.json)
2. Discover and extract programs from countries
Enter your choice (1 or 2): 2

# Select country: Germany
# Output: germany_programs_20260129_143052.json
```

## 📊 Data Collected

Each program includes **comprehensive information**:
- Degree type
- Location and campus city
- Tuition fees
- Application fee
- Program duration
- Success chance rating
- Available intake dates
- Special features (scholarships, fast acceptance, etc.)

## 📁 Output

### Output Files

The scraper generates different files based on the selected mode:

**Option 1 (URL JSON):**
```
programs_from_json_{timestamp}.json       # Complete program data
programs_from_json_{timestamp}_urls.json  # URL list with metadata
```

**Option 2 (Country Discovery):**
```
{country}_programs_{timestamp}.json       # Complete program data
{country}_programs_{timestamp}_urls.json  # URL list with metadata
{country}_batch_N_{timestamp}.json        # Incremental backups (every 50 programs)
{country}_progress.json                   # Resume checkpoint (auto-deleted on success)
```

**File naming examples:**
- `programs_from_json_20260129_143052.json`
- `germany_programs_20260129_143052.json`
- `canada_programs_20260129_143052_urls.json`

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

**Option 1: Extract from URL list**
```bash
$ python scraper.py

🎓 APPLYBOARD PROGRAM SCRAPER
Choose an option:
1. Extract programs from URL JSON file (url.json)
2. Discover and extract programs from countries

Enter your choice (1 or 2): 1
✅ Loaded 50 program URLs from url.json

How many programs to extract (1-50, or 'all'): 20
📊 Will extract 20 program(s)

# Logs in and scrapes 20 programs
# Output: programs_from_json_20260129_143052.json
```

**Option 2: Discover by country**
```bash
$ python scraper.py

🎓 APPLYBOARD PROGRAM SCRAPER
Choose an option:
1. Extract programs from URL JSON file (url.json)
2. Discover and extract programs from countries

Enter your choice (1 or 2): 2

# Select country: Germany
# Discovers 830 programs
# Logs in and scrapes all programs
# Output: germany_programs_20260129_143052.json
```

## ⚙️ Technical Details

### Two Operating Modes

**Mode 1: URL JSON Import**
- Reads program URLs from `url.json` file
- Allows selecting specific number of programs to extract
- Skips URL discovery phase
- Ideal for targeted scraping or re-scraping specific programs

**Mode 2: Country Discovery**
- Automatically discovers all program URLs for selected country
- Automatically switches to 48 items per page for efficiency
- Handles multi-page scraping automatically
- Collects URLs first, then extracts detailed data

### General Features
- Robust error handling for network issues
- Clean, modular code architecture
- Headless browser mode for performance
- Batch saving to prevent data loss
- Resume capability for interrupted scrapes

## 📝 Notes

- Scraping large datasets (500+ programs) may take several minutes
- The scraper respects timeouts to avoid overloading the server
- All data is scraped from publicly available pages

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the scraper.

## 📄 License

This project is for educational purposes.
