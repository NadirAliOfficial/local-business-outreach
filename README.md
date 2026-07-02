# Local Business Outreach Automation

Automated pipeline to find local businesses with no website and send them personalized outreach emails offering web development services.

## How It Works

```
Yelp Scraper → Filter (no website) → Email Finder → Personalized Email → Auto Follow-up
```

## Features

- Scrapes Yelp for businesses across 20+ categories and cities
- Filters only businesses with **no website**
- Finds business emails via Google search
- Sends personalized cold emails with business name, city, category
- Auto follow-up on day 3 and day 7 if no reply
- SQLite database to track all leads and email history
- Daily scheduler runs at 9 AM automatically

## Tech Stack

- Python 3
- Playwright (browser automation)
- BeautifulSoup (HTML parsing)
- Gmail SMTP (email sending)
- SQLite (lead tracking)
- Schedule (daily automation)

## Setup

```bash
pip install playwright requests beautifulsoup4 schedule
python -m playwright install chromium
```

Configure your Gmail credentials in `sender.py`:
```python
GMAIL = 'your@gmail.com'
APP_PASSWORD = 'your_app_password'
```

## Usage

```bash
# Run full pipeline once
python main.py --once

# Run daily at 9 AM
python main.py

# Individual steps
python scraper.py       # scrape leads
python email_finder.py  # find emails
python sender.py        # send initial emails
python sender.py followup  # send follow-ups
```

## Target Markets

- USA (New York, Los Angeles, Chicago, Houston, Phoenix)
- UK (London)
- Canada (Toronto, Vancouver)
- Australia (Sydney, Melbourne)
- UAE (Dubai)
- Germany (Berlin)

## Categories Targeted

Plumbers, Electricians, Barbers, Cleaners, Painters, Locksmiths, Restaurants, Salons, Gyms, Dentists, Hotels, Cafes

## Results

Sends 50 personalized emails per day with 3-day and 7-day follow-ups.

## License

MIT
