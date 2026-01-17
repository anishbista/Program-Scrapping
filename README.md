# ApplyBoard Web Scraper 🎓

A **high-performance** Python web scraper that extracts comprehensive study abroad program data from ApplyBoard.com with advanced features like batch saving, resume capability, and CSV export.

## 🚀 Key Features

### Core Functionality
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

### Step-by-Step Process

1. **Select Country** - Choose from available study destinations:
   ```
   1. Australia
   2. Canada
   3. Germany
   4. Ireland
   5. United Kingdom
   6. United States
   ```

2. **Choose Quantity** - Enter number of programs to scrape:
   ```
   How many programs to scrape? (max 830, or 'all'): 100
   ```

3. **Automatic Login** - Scraper logs in using `.env` credentials

4. **Data Collection** - Scraper extracts data with:
   - Real-time progress updates
   - Batch saving every 50 programs
   - Automatic error recovery

5. **Output Files** - Generates:
   - `{country}_programs_{timestamp}.json` - Complete dataset
   - `{country}_programs_{timestamp}.csv` - Flattened for analysis
   - `{country}_batch_N_{timestamp}.json` - Incremental backups
   - `{country}_progress.json` - Resume checkpoint (auto-deleted on success)

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
