#!/usr/bin/env python3
"""Find emails for businesses using Google search."""
import re, time, random, requests
from bs4 import BeautifulSoup
import db

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
}
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
SKIP_DOMAINS = {'example.com', 'sentry.io', 'wix.com', 'squarespace.com',
                'googleapis.com', 'gstatic.com', 'schema.org'}

def google_search_email(name, city):
    queries = [
        f'"{name}" "{city}" email contact',
        f'"{name}" {city} "@gmail.com" OR "@yahoo.com" OR "info@"',
    ]
    for q in queries:
        try:
            r = requests.get(
                f'https://www.google.com/search?q={requests.utils.quote(q)}&num=5',
                headers=HEADERS, timeout=10
            )
            emails = EMAIL_RE.findall(r.text)
            for e in emails:
                domain = e.split('@')[1].lower()
                if domain not in SKIP_DOMAINS and 'google' not in domain:
                    return e.lower()
            time.sleep(random.uniform(2, 4))
        except Exception:
            pass
    return None

def find_all(limit=50):
    with db.con() as c:
        leads = c.execute(
            "SELECT id, name, city, country FROM leads WHERE (email IS NULL OR email='') LIMIT ?",
            (limit,)
        ).fetchall()

    found = 0
    for lead_id, name, city, country in leads:
        print(f'Finding email: {name} | {city}', flush=True)
        email = google_search_email(name, city)
        if email:
            with db.con() as c:
                c.execute('UPDATE leads SET email=? WHERE id=?', (email, lead_id))
            found += 1
            print(f'  Found: {email}', flush=True)
        else:
            print(f'  Not found', flush=True)
        time.sleep(random.uniform(3, 6))

    print(f'\nFound {found}/{len(leads)} emails')
    return found

if __name__ == '__main__':
    find_all()
