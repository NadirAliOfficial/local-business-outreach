#!/usr/bin/env python3
"""Send outreach emails via Gmail SMTP."""
import smtplib, time, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import db

GMAIL = 'nadiralikhanbusiness@gmail.com'
APP_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD'

INITIAL_SUBJECTS = [
    "Quick question about {name}",
    "{name} — I couldn't find your website",
    "Helping {name} get more customers online",
    "Found {name} on Google Maps — no website?",
]

INITIAL_BODY = """\
Hi {name} team,

I was searching for {category} services in {city} on Google Maps and came across your business — looks great!

I noticed you don't have a website yet. A lot of your potential customers search online before visiting, and without a website you might be losing them to competitors.

I build professional websites for businesses like yours — fast, mobile-friendly, and affordable. I'd love to create a free mockup for {name} so you can see exactly what it could look like before committing to anything.

Would you be open to a quick look?

Best,
Nadir Ali
Web Developer | TEAM NAK
nadiralikhanbusiness@gmail.com
"""

FOLLOWUP_SUBJECTS = [
    "Re: {name} website — just following up",
    "Still happy to build a free mockup for {name}",
]

FOLLOWUP_BODY = """\
Hi again,

Just following up on my previous email about building a website for {name}.

I understand you're busy running your business — I'll keep this short. I can have a free mockup ready for you within 24 hours, no strings attached.

If you're interested, just reply to this email and I'll get started right away.

Best,
Nadir Ali
TEAM NAK
"""

def send_email(to, subject, body):
    msg = MIMEMultipart('alternative')
    msg['From'] = GMAIL
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(GMAIL, APP_PASSWORD)
        s.sendmail(GMAIL, to, msg.as_string())

def send_initial(limit=50):
    leads = db.get_pending_leads()[:limit]
    sent = 0
    for lead_id, name, category, city, country, email in leads:
        try:
            subject = random.choice(INITIAL_SUBJECTS).format(name=name)
            body = INITIAL_BODY.format(name=name, category=category, city=city)
            send_email(email, subject, body)
            db.mark_sent(lead_id, 'initial')
            sent += 1
            print(f'Sent to {name} <{email}>', flush=True)
            time.sleep(random.uniform(30, 60))  # avoid spam filters
        except Exception as e:
            print(f'Failed {email}: {e}', flush=True)
    print(f'\nSent {sent} initial emails')

def send_followups():
    leads = db.get_followup_leads(days=3)
    sent = 0
    for lead_id, name, category, city, country, email in leads:
        try:
            subject = random.choice(FOLLOWUP_SUBJECTS).format(name=name)
            body = FOLLOWUP_BODY.format(name=name)
            send_email(email, subject, body)
            db.mark_sent(lead_id, 'followup1')
            sent += 1
            print(f'Followup to {name} <{email}>', flush=True)
            time.sleep(random.uniform(30, 60))
        except Exception as e:
            print(f'Failed {email}: {e}', flush=True)
    print(f'\nSent {sent} follow-ups')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'followup':
        send_followups()
    else:
        send_initial()
