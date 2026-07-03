#!/usr/bin/env python3
"""Scrape Yelp — visit each business page, filter no-website, grab phone/email."""
import time, re, random, requests
from bs4 import BeautifulSoup
import db

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

TARGETS = [
    ('plumbers', 'New York, NY', 'USA'),
    ('electricians', 'New York, NY', 'USA'),
    ('plumbers', 'Los Angeles, CA', 'USA'),
    ('electricians', 'Chicago, IL', 'USA'),
    ('barbers', 'Chicago, IL', 'USA'),
    ('barbers', 'Houston, TX', 'USA'),
    ('cleaners', 'New York, NY', 'USA'),
    ('cleaners', 'Los Angeles, CA', 'USA'),
    ('painters', 'New York, NY', 'USA'),
    ('painters', 'Chicago, IL', 'USA'),
    ('locksmiths', 'New York, NY', 'USA'),
    ('locksmiths', 'Los Angeles, CA', 'USA'),
    ('plumbers', 'London, UK', 'UK'),
    ('electricians', 'London, UK', 'UK'),
    ('barbers', 'London, UK', 'UK'),
    ('cleaners', 'London, UK', 'UK'),
    ('plumbers', 'Sydney, Australia', 'Australia'),
    ('electricians', 'Melbourne, Australia', 'Australia'),
    ('barbers', 'Toronto, Canada', 'Canada'),
    ('cleaners', 'Toronto, Canada', 'Canada'),
]

def get_biz_links(category, location, pages=5):
    links = []
    for page in range(pages):
        offset = page * 10
        url = f'https://www.yelp.com/search?find_desc={requests.utils.quote(category)}&find_loc={requests.utils.quote(location)}&start={offset}'
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=re.compile(r'^/biz/')):
                href = 'https://www.yelp.com' + a['href'].split('?')[0]
                if href not in links:
                    links.append(href)
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f'  List error: {e}', flush=True)
    return links

def scrape_biz(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Business name
        h1 = soup.find('h1')
        name = h1.get_text(strip=True) if h1 else None
        if not name:
            return None

        # Check for website link — if they have one, skip
        website = soup.find('a', href=re.compile(r'^https?://'), string=re.compile(r'business website|website', re.I))
        if not website:
            # Also check for external links in the sidebar
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                text = a.get_text(strip=True).lower()
                if 'business website' in text or ('website' in text and href.startswith('http') and 'yelp.com' not in href):
                    website = a
                    break

        if website:
            return None  # has website, skip

        # Phone
        phone = ''
        phone_el = soup.find('p', string=re.compile(r'\(\d{3}\)|\+\d'))
        if not phone_el:
            phone_el = soup.find(string=re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}'))
        if phone_el:
            phone = str(phone_el).strip()

        # Email from page — strict validation only
        email = ''
        emails = EMAIL_RE.findall(r.text)
        skip_domains = {'example.com', 'yelp.com', 'sentry.io', 'w3.org',
                        'schema.org', 'yelpcdn.com', 'yji-', 'amazonaws.com',
                        'cloudfront.net', 'facebook.com', 'google.com'}
        skip_exts = {'.png', '.jpg', '.gif', '.svg', '.webp', '.jpeg'}
        for e in emails:
            dom = e.split('@')[1].lower()
            if any(s in dom for s in skip_domains): continue
            if any(dom.endswith(x) for x in skip_exts): continue
            if '2x' in e or 'avatar' in e.lower(): continue
            if len(dom.split('.')[-1]) > 6: continue  # weird TLDs
            email = e.lower()
            break

        return {'name': name, 'phone': phone, 'email': email}
    except Exception:
        return None

def scrape():
    total = 0
    for category, location, country in TARGETS:
        city = location.split(',')[0].strip()
        print(f'\nScraping: {category} in {city}', flush=True)

        links = get_biz_links(category, location, pages=3)
        print(f'  Found {len(links)} listings', flush=True)

        for url in links:
            biz = scrape_biz(url)
            if biz:
                lead_id = db.add_lead(
                    biz['name'], category, city, country,
                    biz['phone'], biz['email'], 'yelp'
                )
                if lead_id:
                    total += 1
                    has_email = '✓ email' if biz['email'] else 'no email'
                    print(f'  + {biz["name"]} | {has_email}', flush=True)
            time.sleep(random.uniform(1, 3))

    print(f'\nTotal new leads (no website): {total}', flush=True)
    print(f'DB: {db.stats()}', flush=True)

if __name__ == '__main__':
    # Clear old leads first
    import sqlite3
    con = sqlite3.connect('/Users/nadirali/leads/leads.db')
    con.execute('DELETE FROM leads')
    con.execute('DELETE FROM emails')
    con.commit()
    con.close()
    print('Cleared old leads, starting fresh...', flush=True)
    scrape()
