# ApplyBoard Scraper Usage Guide

## Quick Start

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the scraper:**
   ```bash
   python scraper.py
   ```

## What the Scraper Does

### Step 1: Fetches Study Destinations
The scraper will automatically fetch all available study destination countries from ApplyBoard.

### Step 2: Country Selection
You'll see a menu like this:
```
==================================================
📚 STUDY DESTINATIONS
==================================================
1. Australia
2. Canada
3. Ireland
4. Germany
5. United Kingdom
6. United States
==================================================

🌍 Select a country (enter number):
```

Enter the number of your chosen country.

### Step 3: Finds Programs Link
The scraper automatically finds the "Explore more programs" link for your selected country.

### Step 4: Shows Total Available Programs
You'll see:
```
📊 Total programs available: 830
```

### Step 5: Choose How Many to Scrape
You'll be asked:
```
How many programs to scrape? (max 830, or 'all'):
```

You can either:
- Enter a number (e.g., `50` to scrape 50 programs)
- Enter `all` to scrape all available programs

### Step 6: Automatic Scraping
The scraper will:
- Automatically set pagination to 48 items per page (maximum)
- Fetch all pages needed to get your requested number of programs
- Extract detailed information for each program
- Show progress as it scrapes

### Step 7: Data Saved to JSON
When complete, you'll see:
```
✅ SCRAPING COMPLETE
📁 Data saved to: germany_programs_20260115_143052.json
📊 Total programs: 50
```

## Data Extracted

For each program, the scraper collects:

- **School Information:**
  - School name
  - School URL
  
- **Program Details:**
  - Program name
  - Program URL
  - Degree type (e.g., Master's Degree, Bachelor's Degree)
  
- **Costs & Duration:**
  - Location (city, country)
  - Campus city
  - Tuition (1st year)
  - Application fee
  - Duration (in months)
  
- **Admission Info:**
  - Success chance (High/Medium/Low)
  - Available intakes (e.g., Mar 2026, Sep 2026)
  
- **Special Features:**
  - Fast Acceptance
  - Scholarships Available
  - etc.

## JSON Output Format

```json
{
  "scraped_at": "2026-01-15T14:30:52.123456",
  "source_url": "https://www.applyboard.com",
  "total_items": 50,
  "data": [
    {
      "school_name": "Hochschulen Fresenius - Berlin",
      "school_url": "/schools/hochschulen-fresenius-berlin",
      "degree_type": "Master's Degree",
      "program_name": "Master of Science - Industrial Engineering & International Management",
      "program_url": "/schools/hochschulen-fresenius-berlin/programs/...",
      "location": "Berlin, GERMANY",
      "campus_city": "Berlin",
      "tuition_(1st_year)": "€11,400 EUR",
      "application_fee": "Free",
      "duration": "24 months",
      "success_chance": "High",
      "available_intakes": ["Mar 2026", "Sep 2026", "Mar 2028"],
      "features": ["Fast Acceptance"]
    }
  ]
}
```

## Tips

1. **Start Small:** Try scraping 10-20 programs first to test the setup
2. **All Programs:** Use `all` to get complete data for a country
3. **Be Patient:** Scraping large datasets (800+ programs) may take several minutes
4. **Check Output:** Open the JSON file to view all scraped data

## Troubleshooting

- **Connection Errors:** Check your internet connection
- **No countries found:** The website structure may have changed
- **Missing data:** Some programs may not have all fields available

## Example Session

```bash
$ python scraper.py

Fetching study destinations...
✓ Found 6 countries

==================================================
📚 STUDY DESTINATIONS
==================================================
1. Australia
2. Canada
3. Ireland
4. Germany
5. United Kingdom
6. United States
==================================================

🌍 Select a country (enter number): 4

✓ Selected: Germany
📍 URL: https://www.applyboard.com/germany

Fetching country page: https://www.applyboard.com/germany
✓ Found programs link: https://www.applyboard.com/search?filter...

Fetching programs page: https://www.applyboard.com/search?...
📊 Total programs available: 830

==================================================
How many programs to scrape? (max 830, or 'all'): 50
🎯 Will scrape 50 programs
==================================================

📄 Scraping page 1...
   Found 48 programs on this page
   ✓ Scraped: Master of Science - Industrial Engineering & International M...
   ✓ Scraped: Master of Science - International Business Management...
   ...

📄 Scraping page 2...
   Found 48 programs on this page
   ✓ Scraped: Master of Science - Computer Science (120 credit points)...
   ...

✅ Total programs scraped: 50

==================================================
✅ SCRAPING COMPLETE
==================================================
📁 Data saved to: germany_programs_20260115_143052.json
📊 Total programs: 50
```
