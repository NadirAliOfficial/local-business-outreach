import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'leads.db'

def init():
    con = sqlite3.connect(DB)
    con.executescript('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            city TEXT,
            country TEXT,
            phone TEXT,
            email TEXT,
            source TEXT,
            status TEXT DEFAULT 'new',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY,
            lead_id INTEGER,
            type TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        );
    ''')
    con.commit()
    con.close()

def con():
    return sqlite3.connect(DB)

def add_lead(name, category, city, country, phone, email, source):
    with con() as c:
        existing = c.execute('SELECT id FROM leads WHERE name=? AND city=?', (name, city)).fetchone()
        if existing:
            return None
        cur = c.execute(
            'INSERT INTO leads (name,category,city,country,phone,email,source) VALUES (?,?,?,?,?,?,?)',
            (name, category, city, country, phone, email, source)
        )
        return cur.lastrowid

def get_pending_leads():
    with con() as c:
        return c.execute('''
            SELECT l.id, l.name, l.category, l.city, l.country, l.email
            FROM leads l
            WHERE l.email IS NOT NULL AND l.email != ''
            AND l.status = 'new'
            AND l.id NOT IN (SELECT lead_id FROM emails WHERE type='initial')
        ''').fetchall()

def get_followup_leads(days=3):
    with con() as c:
        return c.execute(f'''
            SELECT l.id, l.name, l.category, l.city, l.country, l.email
            FROM leads l
            JOIN emails e ON e.lead_id = l.id AND e.type='initial'
            WHERE l.status = 'new'
            AND l.id NOT IN (SELECT lead_id FROM emails WHERE type='followup1')
            AND e.sent_at < datetime('now', '-{days} days')
        ''').fetchall()

def mark_sent(lead_id, email_type):
    with con() as c:
        c.execute('INSERT INTO emails (lead_id, type) VALUES (?,?)', (lead_id, email_type))

def mark_replied(lead_id):
    with con() as c:
        c.execute("UPDATE leads SET status='replied' WHERE id=?", (lead_id,))

def stats():
    with con() as c:
        total = c.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
        with_email = c.execute("SELECT COUNT(*) FROM leads WHERE email!='' AND email IS NOT NULL").fetchone()[0]
        sent = c.execute("SELECT COUNT(DISTINCT lead_id) FROM emails WHERE type='initial'").fetchone()[0]
        replied = c.execute("SELECT COUNT(*) FROM leads WHERE status='replied'").fetchone()[0]
        return {'total': total, 'with_email': with_email, 'sent': sent, 'replied': replied}

init()
