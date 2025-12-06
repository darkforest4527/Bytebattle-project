import os
import datetime
import uuid
from flask import Flask, request, redirect, url_for, flash, get_flashed_messages, session
from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash

# --- CONFIGURATION ---
app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions'

# --- DATABASE SETUP (Local, No-SQL) ---
db = TinyDB('db.json')
clubs_table = db.table('clubs')
events_table = db.table('events')
users_table = db.table('users')
registrations_table = db.table('registrations')

# --- INITIALIZE SAMPLE DATA ---
def initialize_sample_data():
    """
    Populates the database with sample clubs and events if it is empty.
    """
    if not clubs_table.all():
        print("Initializing sample clubs...")
        clubs_table.insert_multiple([
            {
                'name': 'Campus Tech',
                'description': 'Coding, gadgets, and all things tech. We host hackathons and workshops.',
                'leader': 'Alice System',
                'founded': '2023-01-15',
                'created_by': 'system'
            },
            {
                'name': 'Drama Club',
                'description': 'Theater, improv, and stage production. Come express yourself!',
                'leader': 'Bob System',
                'founded': '2023-03-10',
                'created_by': 'system'
            },
            {
                'name': 'Green Earth',
                'description': 'Sustainability initiatives and community gardening.',
                'leader': 'Charlie Green',
                'founded': '2023-04-22',
                'created_by': 'system'
            }
        ])

    if not events_table.all():
        print("Initializing sample events...")
        today = datetime.date.today()
        events_table.insert_multiple([
            {
                'id': str(uuid.uuid4()),
                'title': 'Mega Hackathon 2025',
                'club_name': 'Campus Tech',
                'type': 'Competition',
                'date': (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"),
                'location': 'Engineering Block A',
                'description': 'A 24-hour coding marathon. Build amazing projects and win prizes! Open to all majors.',
                'created_by': 'system'
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Improv Comedy Night',
                'club_name': 'Drama Club',
                'type': 'Comedy',
                'date': (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
                'location': 'Student Center Auditorium',
                'description': 'Join us for a night of laughs! Audience participation is encouraged but not required.',
                'created_by': 'system'
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Python Workshop',
                'club_name': 'Campus Tech',
                'type': 'Workshop',
                'date': (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
                'location': 'Lab 304',
                'description': 'Learn the basics of Python programming. No prior experience needed. Bring your laptop!',
                'created_by': 'system'
            },
             {
                'id': str(uuid.uuid4()),
                'title': 'Community Garden Cleanup',
                'club_name': 'Green Earth',
                'type': 'Social',
                'date': (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                'location': 'North Garden',
                'description': 'Help us prepare the garden for spring planting. Snacks provided!',
                'created_by': 'system'
            }
        ])

# --- TEMPLATES (HTML/CSS Strings) ---
STYLES = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    :root {
        /* Light Theme (Default) */
        --primary: #0d9488; /* Teal-600 */
        --primary-dark: #0f766e; /* Teal-700 */
        --secondary: #14b8a6; /* Teal-500 */
        --danger: #ef4444;
        --success: #10b981;
        --bg: #f8fafc; /* Slate-50 */
        --card-bg: #ffffff;
        --text-main: #334155; /* Slate-700 */
        --text-muted: #64748b; /* Slate-500 */
        --border: #e2e8f0; /* Slate-200 */
        --input-bg: #ffffff;
        --nav-bg: #ffffff;
        --footer-bg: #ffffff;
    }

    [data-theme="dark"] {
        /* Dark Theme overrides */
        --primary: #2dd4bf; /* Teal-400 (Lighter for dark mode contrast) */
        --primary-dark: #0d9488; /* Teal-600 */
        --secondary: #5eead4; /* Teal-300 */
        --bg: #0f172a; /* Slate 900 */
        --card-bg: #1e293b; /* Slate 800 */
        --text-main: #f1f5f9; /* Slate 100 */
        --text-muted: #94a3b8; /* Slate 400 */
        --border: #334155; /* Slate 700 */
        --input-bg: #1e293b;
        --nav-bg: #1e293b;
        --footer-bg: #1e293b;
    }
    
    * { box-sizing: border-box; transition: background-color 0.3s ease, border-color 0.3s ease; }

    body { 
        background-color: var(--bg); 
        font-family: 'Inter', sans-serif; 
        color: var(--text-main); 
        margin: 0; 
        line-height: 1.6;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        -webkit-font-smoothing: antialiased;
    }
    
    .main-content {
        flex: 1;
        width: 100%;
    }

    /* Navbar */
    .nav { 
        background-color: var(--nav-bg); 
        border-bottom: 1px solid var(--border); 
        padding: 1rem 0; 
        position: sticky; 
        top: 0; 
        z-index: 50; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .nav-container { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        max-width: 1200px; 
        margin: 0 auto; 
        padding: 0 1.5rem; 
    }
    .nav-brand { 
        font-size: 1.5rem; 
        font-weight: 800; 
        color: var(--primary); 
        text-decoration: none; 
        letter-spacing: -0.025em;
    }
    .nav-links { display: flex; align-items: center; gap: 1.5rem; }
    
    /* Standard Links */
    .nav a.nav-text-link { 
        color: var(--text-muted); 
        text-decoration: none; 
        font-weight: 500; 
        transition: color 0.2s; 
        font-size: 0.95rem; 
    }
    .nav a.nav-text-link:hover { color: var(--primary); }
    
    /* Hero Section - Teal/Emerald Gradient */
    .hero { 
        background: linear-gradient(135deg, #115e59 0%, #0d9488 100%); /* Deep Teal */
        padding: 5rem 1.5rem; 
        text-align: center; 
        margin-bottom: 3rem;
        color: white;
    }
    .hero h1 { 
        margin: 0; 
        font-size: 3.5rem; 
        font-weight: 900; 
        letter-spacing: -0.04em; 
        line-height: 1.1; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: white; 
    }
    .hero p { 
        font-size: 1.35rem; 
        color: rgba(255, 255, 255, 0.9); 
        margin-top: 1.5rem; 
        max-width: 700px; 
        margin-left: auto; 
        margin-right: auto; 
        font-weight: 400;
    }

    /* Layout */
    .container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }
    .grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); 
        gap: 2rem; 
    }

    /* Footer */
    .site-footer {
        background-color: var(--footer-bg);
        border-top: 1px solid var(--border);
        padding: 3rem 0;
        margin-top: 5rem;
        color: var(--text-muted);
    }
    .footer-content {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
    }
    .footer-col h4 { color: var(--text-main); margin-top: 0; }
    .footer-col ul { list-style: none; padding: 0; }
    .footer-col li { margin-bottom: 0.5rem; }
    .footer-col a { color: var(--text-muted); text-decoration: none; font-size: 0.9rem; }
    .footer-col a:hover { color: var(--primary); }
    .copyright {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        font-size: 0.875rem;
    }

    /* Cards */
    .card { 
        background: var(--card-bg); 
        border-radius: 0.75rem; 
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        padding: 1.75rem; 
        transition: all 0.3s ease; 
        border: 1px solid var(--border); 
        display: flex; 
        flex-direction: column; 
        height: 100%; 
        position: relative;
        overflow: hidden;
    }
    .card:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1); 
    }
    /* Simple solid accent line */
    .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--primary);
    }
    
    .card-header-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; margin-top: 0.5rem;}
    .card-title { margin: 0; font-size: 1.25rem; font-weight: 700; color: var(--text-main); line-height: 1.3; }
    .card-host { font-size: 0.875rem; color: var(--primary); font-weight: 600; margin-bottom: 1rem; display: block; }
    .card-body { color: var(--text-muted); margin-bottom: 1.5rem; flex-grow: 1; font-size: 0.95rem; }
    
    .card-meta { 
        border-top: 1px solid var(--border); 
        padding-top: 1rem; 
        margin-top: auto; 
        display: flex; 
        justify-content: space-between; 
        color: var(--text-muted); 
        font-size: 0.875rem; 
        font-weight: 500; 
    }
    .card-actions { margin-top: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; }

    /* Buttons */
    .btn { 
        display: inline-flex; 
        align-items: center; 
        justify-content: center; 
        padding: 0.75rem 1.25rem; 
        border-radius: 0.5rem; 
        text-decoration: none; 
        font-weight: 600; 
        cursor: pointer; 
        border: none; 
        font-size: 0.95rem; 
        transition: all 0.2s; 
        width: 100%;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .btn-auto { width: auto; }
    .btn-primary { 
        background-color: var(--primary); 
        color: white !important; /* Force white text */
    }
    .btn-primary:hover { 
        background-color: var(--primary-dark); 
        transform: translateY(-1px);
    }
    .btn-success { background-color: var(--success); color: white; }
    .btn-danger { background-color: transparent; color: var(--danger); border: 1px solid var(--danger); font-size: 0.85rem; padding: 0.4rem; box-shadow: none; }
    .btn-danger:hover { background-color: rgba(239, 68, 68, 0.05); }
    .btn-outline { border: 1px solid var(--border); color: var(--text-main); background: transparent; box-shadow: none;}
    .btn-outline:hover { border-color: var(--text-muted); background-color: rgba(0,0,0,0.02); }
    
    /* Nav Button Specifics - High Visibility */
    .btn-nav-primary { 
        background-color: var(--primary); 
        color: white !important; /* Force white text */
        padding: 0.6rem 1.4rem; 
        border-radius: 9999px; 
        font-size: 0.95rem; 
        font-weight: 700; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-decoration: none !important;
        border: 2px solid var(--primary);
    }
    .btn-nav-primary:hover { 
        background-color: var(--primary-dark); 
        border-color: var(--primary-dark);
        transform: translateY(-1px); 
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }

    .btn-nav-secondary {
        background-color: transparent;
        color: var(--primary) !important;
        padding: 0.6rem 1.4rem;
        border-radius: 9999px;
        font-size: 0.95rem;
        font-weight: 700;
        border: 2px solid var(--border);
        text-decoration: none !important;
        margin-left: 0.5rem;
    }
    .btn-nav-secondary:hover {
        border-color: var(--primary);
        background-color: rgba(13, 148, 136, 0.05); /* Teal hint */
        transform: translateY(-1px);
    }
    
    .btn-registered { background-color: transparent; color: var(--success); border: 2px solid var(--success); box-shadow: none; }
    .btn-registered:hover { background-color: rgba(16, 185, 129, 0.05); content: "Unregister"; }

    /* Theme Toggle Button */
    .theme-toggle-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text-muted);
        cursor: pointer;
        font-size: 1.1rem;
        padding: 0.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        width: 40px;
        height: 40px;
    }
    .theme-toggle-btn:hover {
        background-color: rgba(0,0,0,0.02);
        color: var(--primary);
        border-color: var(--primary);
    }

    /* Tags - Subdued Pastels */
    .tag { font-size: 0.75rem; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; border: 1px solid transparent;}
    .tag-Competition { background-color: #fff7ed; color: #9a3412; border-color: #ffedd5; } /* Orange-50 */
    .tag-Comedy { background-color: #f0fdf4; color: #166534; border-color: #dcfce7; } /* Green-50 */
    .tag-Workshop { background-color: #eff6ff; color: #1e40af; border-color: #dbeafe; } /* Blue-50 */
    .tag-Seminar { background-color: #f8fafc; color: #475569; border-color: #e2e8f0; } /* Slate-50 */
    .tag-Social { background-color: #fdf2f8; color: #9d174d; border-color: #fce7f3; } /* Pink-50 */
    .tag-Other { background-color: #f8fafc; color: #475569; border-color: #e2e8f0; }

    /* Forms */
    .form-container { max-width: 450px; margin: 3rem auto; }
    .form-group { margin-bottom: 1.5rem; }
    .form-control { 
        width: 100%; 
        padding: 0.75rem; 
        margin-top: 0.5rem; 
        border: 1px solid var(--border); 
        border-radius: 0.5rem; 
        font-size: 1rem; 
        font-family: inherit; 
        background-color: var(--input-bg);
        color: var(--text-main);
        transition: border-color 0.2s;
    }
    .form-control:focus { outline: none; border-color: var(--primary); ring: 2px solid var(--primary); }
    label { font-weight: 600; color: var(--text-main); font-size: 0.95rem; }

    /* Alerts */
    .alert { padding: 1rem; margin-bottom: 2rem; border-radius: 0.5rem; font-weight: 500; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .alert-success { background-color: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
    .alert-danger { background-color: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .alert-info { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    
    .empty-state { text-align: center; padding: 6rem 1rem; color: var(--text-muted); }
</style>
"""

def render_page(content, hero_html=""):
    messages = get_flashed_messages(with_categories=True)
    msg_html = ""
    if messages:
        for category, message in messages:
            css_class = 'alert-danger' if category == 'error' else 'alert-success'
            if category == 'info': css_class = 'alert-info'
            msg_html += f'<div class="alert {css_class}">{message}</div>'
    
    if 'username' in session:
        nav_links = f"""
            <span style="color: var(--text-muted); font-size: 0.9rem;">Hi, <strong>{session['username']}</strong></span>
            <a href="/logout" class="nav-text-link">Logout</a>
            <a href="/" class="nav-text-link">Events</a>
            <a href="/clubs" class="nav-text-link">Clubs</a>
            <a href="/create_event" class="btn-nav-primary">Host Event</a>
        """
    else:
        nav_links = """
            <a href="/" class="nav-text-link">Events</a>
            <a href="/clubs" class="nav-text-link">Clubs</a>
            <a href="/login" class="btn-nav-secondary">Log In</a>
            <a href="/signup" class="btn-nav-primary">Sign Up</a>
        """

    footer_html = """
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-col" style="flex: 2; min-width: 250px;">
                    <h4 style="color: var(--primary); font-weight: 800; font-size: 1.2rem;">ClubHub</h4>
                    <p>The central platform for campus communities to connect, organize, and thrive.</p>
                </div>
                <div class="footer-col">
                    <h4>Discover</h4>
                    <ul>
                        <li><a href="/">All Events</a></li>
                        <li><a href="/clubs">Club Directory</a></li>
                        <li><a href="#">Featured Hosts</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Community</h4>
                    <ul>
                        <li><a href="#">Guidelines</a></li>
                        <li><a href="#">Safety Center</a></li>
                        <li><a href="#">Support</a></li>
                    </ul>
                </div>
            </div>
            <div class="copyright">
                &copy; 2025 ClubHub Campus System. All rights reserved.
            </div>
        </div>
    </footer>
    <script>
        // --- Theme Toggle Logic ---
        document.addEventListener('DOMContentLoaded', () => {
            const toggleBtn = document.getElementById('theme-toggle');
            const html = document.documentElement;
            const icon = document.getElementById('theme-icon');

            // 1. Check local storage
            const savedTheme = localStorage.getItem('theme') || 'light';
            html.setAttribute('data-theme', savedTheme);
            updateIcon(savedTheme);

            // 2. Toggle function
            toggleBtn.addEventListener('click', () => {
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                updateIcon(newTheme);
            });

            function updateIcon(theme) {
                icon.textContent = theme === 'light' ? '🌙' : '☀️';
            }
        });
    </script>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Campus Club Hub</title>
        {STYLES}
    </head>
    <body>
        <nav class="nav">
            <div class="nav-container">
                <a href="/" class="nav-brand">ClubHub</a>
                <div class="nav-links">
                    {nav_links}
                    <button id="theme-toggle" class="theme-toggle-btn" title="Toggle Dark Mode">
                        <span id="theme-icon">🌙</span>
                    </button>
                </div>
            </div>
        </nav>
        
        <div class="main-content">
            {hero_html}
            <div class="container" style="margin-top: 2rem;">{msg_html}</div>
            {content}
        </div>
        
        {footer_html}
    </body>
    </html>
    """

# --- ERROR HANDLER ---
@app.errorhandler(404)
def page_not_found(e):
    content = """
    <div class="container" style="text-align:center; margin-top:4rem;">
        <h1 style="font-size:4rem; color: var(--primary); margin-bottom: 1rem;">404</h1>
        <h3 style="margin-bottom: 1rem;">Page Not Found</h3>
        <p style="color: var(--text-muted); margin-bottom: 2rem;">The page you are looking for doesn't exist or has moved.</p>
        <a href="/" class="btn btn-primary btn-auto">Return Home</a>
    </div>
    """
    return render_page(content), 404

# --- AUTH ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        User = Query()
        if users_table.search(User.username == username):
            flash('Username already exists', 'error')
        else:
            users_table.insert({'username': username, 'password': generate_password_hash(password)})
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
            
    content = """
    <div class="form-container">
        <div class="card">
            <h2 style="text-align:center; margin-bottom: 1.5rem; color: var(--text-main);">Join ClubHub</h2>
            <form method="POST">
                <div class="form-group"><label>Username</label><input type="text" name="username" class="form-control" required placeholder="Choose a username"></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" class="form-control" required placeholder="Choose a password"></div>
                <button type="submit" class="btn btn-success" style="width:100%">Create Account</button>
            </form>
            <p style="text-align:center; margin-top:1.5rem; color: var(--text-muted);">Already have an account? <a href="/login" style="color: var(--primary); font-weight:600; text-decoration:none;">Log in</a></p>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        User = Query()
        user = users_table.search(User.username == username)
        if user and check_password_hash(user[0]['password'], password):
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    content = """
    <div class="form-container">
        <div class="card">
            <h2 style="text-align:center; margin-bottom: 1.5rem; color: var(--text-main);">Welcome Back</h2>
            <form method="POST">
                <div class="form-group"><label>Username</label><input type="text" name="username" class="form-control" required></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" class="form-control" required></div>
                <button type="submit" class="btn btn-primary" style="width:100%">Sign In</button>
            </form>
            <p style="text-align:center; margin-top:1.5rem; color: var(--text-muted);">New here? <a href="/signup" style="color: var(--primary); font-weight:600; text-decoration:none;">Create an account</a></p>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- APP ROUTES ---
@app.route('/')
def home():
    current_user = session.get('username')
    all_events = events_table.all()
    
    # Auto-migrate
    for event in all_events:
        if 'id' not in event:
            new_id = str(uuid.uuid4())
            events_table.update({'id': new_id}, Query().title == event['title'])
            event['id'] = new_id

    events = sorted(all_events, key=lambda x: x.get('date', '9999-99-99'))
    
    my_registrations = []
    if current_user:
        Registration = Query()
        regs = registrations_table.search(Registration.username == current_user)
        my_registrations = [r['event_id'] for r in regs]

    hero_section = """
    <div class="hero">
        <div class="container">
            <h1>Campus Life, Elevated.</h1>
            <p>Your one-stop destination for university events, clubs, and competitions. Don't miss out on what's happening today.</p>
        </div>
    </div>
    """

    events_html = ""
    if not events:
        events_html = """
        <div class="empty-state">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🗓️</div>
            <h3>No events scheduled yet.</h3>
            <p>Be the spark! Create the first event on campus.</p>
            <a href="/create_event" class="btn btn-primary btn-auto" style="margin-top: 1rem;">Host an Event</a>
        </div>
        """
    else:
        events_html = '<div class="grid">'
        for event in events:
            type_str = event.get('type', 'Other')
            tag_class = f"tag-{type_str.split()[0]}" if type_str else "tag-Other"
            
            delete_btn = ""
            if current_user and event.get('created_by') == current_user:
                delete_btn = f"""
                <form action="/delete_event/{event.get('id')}" method="POST" onsubmit="return confirm('Are you sure you want to delete this event?');">
                    <button type="submit" class="btn btn-danger" style="width:100%">🗑 Delete Event</button>
                </form>
                """

            if not current_user:
                main_btn = '<a href="/login" class="btn btn-outline" style="width:100%">Login to Register</a>'
            elif event.get('id') in my_registrations:
                # UNREGISTER BUTTON LOGIC
                main_btn = f"""
                <form action="/unregister_from_event/{event.get('id')}" method="POST" onsubmit="return confirm('Do you want to unregister from this event?');">
                    <button type="submit" class="btn btn-registered" style="width:100%">✓ Registered (Undo)</button>
                </form>
                """
            else:
                main_btn = f"""
                <form action="/register_for_event/{event.get('id')}" method="POST">
                    <button type="submit" class="btn btn-primary" style="width:100%">Register Now</button>
                </form>
                """

            events_html += f"""
            <div class="card">
                <div class="card-header-row">
                    <h3 class="card-title">{event.get('title')}</h3>
                    <span class="tag {tag_class}">{event.get('type')}</span>
                </div>
                <span class="card-host">by {event.get('club_name')}</span>
                
                <div class="card-body">
                    {event.get('description')}
                </div>
                
                <div class="card-meta">
                    <span>📅 {event.get('date')}</span>
                    <span>📍 {event.get('location')}</span>
                </div>
                
                <div class="card-actions">
                    {main_btn}
                    {delete_btn}
                </div>
            </div>
            """
        events_html += '</div>'

    page_content = f"""<div class="container">{events_html}</div>"""
    return render_page(page_content, hero_html=hero_section)

@app.route('/delete_event/<event_id>', methods=['POST'])
def delete_event(event_id):
    if 'username' not in session:
        flash('You must be logged in to do that.', 'error')
        return redirect(url_for('login'))
    
    target_event = events_table.get(Query().id == event_id)
    if target_event and target_event.get('created_by') == session['username']:
        events_table.remove(doc_ids=[target_event.doc_id])
        registrations_table.remove(Query().event_id == event_id)
        flash('Event deleted successfully.', 'success')
    else:
        flash('Authorization failed or event not found.', 'error')
        
    return redirect(url_for('home'))

@app.route('/register_for_event/<event_id>', methods=['POST'])
def register_for_event(event_id):
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    
    Registration = Query()
    if registrations_table.search((Registration.event_id == event_id) & (Registration.username == user)):
        flash('You are already registered for this event.', 'info')
    else:
        registrations_table.insert({
            'event_id': event_id,
            'username': user,
            'timestamp': str(datetime.datetime.now())
        })
        flash('Successfully registered for the event!', 'success')
    return redirect(url_for('home'))

@app.route('/unregister_from_event/<event_id>', methods=['POST'])
def unregister_from_event(event_id):
    if 'username' not in session: return redirect(url_for('login'))
    user = session['username']
    
    Registration = Query()
    # Remove entry where both event_id and username match
    registrations_table.remove((Registration.event_id == event_id) & (Registration.username == user))
    
    flash('Successfully unregistered from event.', 'info')
    return redirect(url_for('home'))

@app.route('/clubs')
def list_clubs():
    current_user = session.get('username')
    clubs = clubs_table.all()
    clubs_html = ""
    reg_button = '<a href="/register_club" class="btn btn-outline btn-auto">+ Register New Club</a>'
    
    if not clubs:
        clubs_html = '<div class="empty-state"><h3>No clubs registered yet.</h3><p>Start a new community today!</p></div>'
    else:
        clubs_html = '<div class="grid">'
        for club in clubs:
            delete_btn = ""
            if current_user and club.get('created_by') == current_user:
                delete_btn = f"""
                <div style="margin-top: 1rem; border-top: 1px solid #f3f4f6; padding-top: 1rem;">
                    <form action="/delete_club/{club.get('name')}" method="POST" onsubmit="return confirm('Delete this club and ALL its events?');">
                        <button type="submit" class="btn btn-danger" style="width:100%">🗑 Delete Club</button>
                    </form>
                </div>
                """
                
            clubs_html += f"""
            <div class="card">
                <div class="card-header-row">
                    <h3 class="card-title">{club.get('name')}</h3>
                    <small style="color:var(--text-muted);">Est. {club.get('founded')}</small>
                </div>
                <span class="card-host">Leader: {club.get('leader')}</span>
                <div class="card-body">
                    {club.get('description')}
                </div>
                {delete_btn}
            </div>
            """
        clubs_html += '</div>'
            
    page_content = f"""
    <div class="container" style="margin-top: 2rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem;">
            <h2 style="margin:0; font-size: 2rem;">Registered Clubs</h2>
            {reg_button}
        </div>
        {clubs_html}
    </div>
    """
    
    hero_section = """
    <div class="hero" style="padding: 3rem 1.5rem; margin-bottom: 0;">
        <div class="container">
            <h1>Communities</h1>
            <p>Find your tribe. Join a club.</p>
        </div>
    </div>
    """
    return render_page(page_content, hero_html=hero_section)

@app.route('/delete_club/<club_name>', methods=['POST'])
def delete_club(club_name):
    if 'username' not in session: return redirect(url_for('login'))
    
    Club = Query()
    target_club = clubs_table.get(Club.name == club_name)
    
    if target_club and target_club.get('created_by') == session['username']:
        clubs_table.remove(doc_ids=[target_club.doc_id])
        events_table.remove(Query().club_name == club_name)
        flash(f'Club "{club_name}" deleted.', 'success')
    else:
        flash('Authorization failed.', 'error')
    return redirect(url_for('list_clubs'))

@app.route('/register_club', methods=['GET', 'POST'])
def register_club():
    if 'username' not in session: return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        if clubs_table.search(Query().name == name):
            flash('Club name already exists!', 'error')
        else:
            clubs_table.insert({
                'name': name,
                'description': request.form.get('description'),
                'leader': request.form.get('leader'),
                'founded': datetime.date.today().strftime("%Y-%m-%d"),
                'created_by': session['username']
            })
            flash('Club registered!', 'success')
            return redirect(url_for('list_clubs'))

    content = """
    <div class="form-container">
        <div class="card">
            <h2 style="margin-top:0; color: var(--text-main);">Register a New Club</h2>
            <form method="POST">
                <div class="form-group"><label>Club Name</label><input type="text" name="name" class="form-control" required placeholder="e.g. Robotics Society"></div>
                <div class="form-group"><label>Description</label><textarea name="description" class="form-control" rows="3" required placeholder="Mission statement..."></textarea></div>
                <div class="form-group"><label>Club Leader</label><input type="text" name="leader" class="form-control" required></div>
                <button type="submit" class="btn btn-success" style="width:100%">Register Club</button>
            </form>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'username' not in session: return redirect(url_for('login'))

    clubs = clubs_table.all()
    if request.method == 'POST':
        events_table.insert({
            'id': str(uuid.uuid4()),
            'title': request.form.get('title'),
            'club_name': request.form.get('club_name'),
            'type': request.form.get('type'),
            'date': request.form.get('date'),
            'location': request.form.get('location'),
            'description': request.form.get('description'),
            'created_by': session['username']
        })
        flash('Event created!', 'success')
        return redirect(url_for('home'))

    if not clubs:
        return render_page('<div class="container" style="margin-top:40px;"><div class="alert alert-danger">No clubs found. <a href="/register_club">Register one here</a>.</div></div>')

    club_options = "".join([f'<option value="{c["name"]}">{c["name"]}</option>' for c in clubs])
    content = f"""
    <div class="form-container">
        <div class="card">
            <h2 style="margin-top:0; color: var(--text-main);">Create an Event</h2>
            <form method="POST">
                <div class="form-group"><label>Event Title</label><input type="text" name="title" class="form-control" required placeholder="e.g. Annual Hackathon"></div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div class="form-group"><label>Hosting Club</label><select name="club_name" class="form-control" required>{club_options}</select></div>
                    <div class="form-group"><label>Event Type</label>
                        <select name="type" class="form-control" required>
                            <option value="Competition">Competition</option>
                            <option value="Comedy">Stand-up Comedy</option>
                            <option value="Workshop">Workshop</option>
                            <option value="Seminar">Seminar</option>
                            <option value="Social">Social Gathering</option>
                        </select>
                    </div>
                </div>
                <div class="form-group"><label>Date</label><input type="date" name="date" class="form-control" required></div>
                <div class="form-group"><label>Location</label><input type="text" name="location" class="form-control" required placeholder="e.g. Main Auditorium"></div>
                <div class="form-group"><label>Description</label><textarea name="description" class="form-control" rows="3" required placeholder="Describe the event..."></textarea></div>
                <button type="submit" class="btn btn-primary" style="width:100%">Publish Event</button>
            </form>
        </div>
    </div>
    """
    return render_page(content)

if __name__ == '__main__':
    initialize_sample_data()
    app.run(debug=True)