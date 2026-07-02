#!/usr/bin/env python3
"""Main orchestrator — runs full pipeline daily."""
import time, schedule
import db, scraper, email_finder, sender

def run_pipeline():
    print('\n=== Pipeline started ===', flush=True)
    print(f'Stats before: {db.stats()}', flush=True)

    print('\n[1/3] Scraping Google Maps...', flush=True)
    scraper.scrape(max_per_search=20)

    print('\n[2/3] Finding emails...', flush=True)
    email_finder.find_all(limit=100)

    print('\n[3/3] Sending emails...', flush=True)
    sender.send_initial(limit=50)
    sender.send_followups()

    print(f'\nStats after: {db.stats()}', flush=True)
    print('=== Pipeline done ===\n', flush=True)

if __name__ == '__main__':
    import sys
    if '--once' in sys.argv:
        run_pipeline()
    else:
        # Run once at startup then daily at 9 AM
        run_pipeline()
        schedule.every().day.at('09:00').do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(60)
