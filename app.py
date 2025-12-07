import os
import datetime
import uuid
from flask import Flask, request, redirect, url_for, flash, get_flashed_messages, session, jsonify
from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions_replace_in_production'


db_path = 'db.json'
db = TinyDB(db_path)
clubs_table = db.table('clubs')
events_table = db.table('events')
users_table = db.table('users')
registrations_table = db.table('registrations')


def initialize_system():
    print("--- SYSTEM STARTUP ---")
    User = Query()
    
    if not users_table.search(User.username == 'admin'):
        users_table.insert({'username': 'admin', 'password': generate_password_hash('123'), 'role': 'admin'})
    if not users_table.search(User.username == 'student'):
        users_table.insert({'username': 'student', 'password': generate_password_hash('123'), 'role': 'student'})

    if not clubs_table.all():
        clubs_table.insert_multiple([
            {'name': 'Campus Tech', 'description': 'Coding, gadgets, and all things tech. We host hackathons and workshops.', 'leader': 'Alice Admin', 'founded': '2023-01-15', 'created_by': 'admin'},
            {'name': 'Drama Club', 'description': 'Theater and improv.', 'leader': 'Bob Admin', 'founded': '2023-03-10', 'created_by': 'admin'},
            {'name': 'Green Earth', 'description': 'Sustainability & Gardening.', 'leader': 'Charlie Green', 'founded': '2023-04-22', 'created_by': 'admin'}
        ])

    if not events_table.all():
        today = datetime.date.today()
        events_table.insert_multiple([
            {'id': str(uuid.uuid4()), 'title': 'Mega Hackathon 2025', 'club_name': 'Campus Tech', 'type': 'Competition', 'date': (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d"), 'location': 'Eng Block A', 'description': '24h coding marathon.', 'created_by': 'admin'},
            {'id': str(uuid.uuid4()), 'title': 'Improv Night', 'club_name': 'Drama Club', 'type': 'Comedy', 'date': (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), 'location': 'Auditorium', 'description': 'Laugh with us!', 'created_by': 'admin'},
            {'id': str(uuid.uuid4()), 'title': 'Garden Cleanup', 'club_name': 'Green Earth', 'type': 'Social', 'date': (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d"), 'location': 'North Garden', 'description': 'Snacks provided!', 'created_by': 'admin'}
        ])
    print("--- SYSTEM READY ---")

# --- FRONTEND STYLES (CSS) ---
STYLES = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap" rel="stylesheet">
<style>
    :root {
        --primary: #0d9488; --primary-dark: #0f766e; --secondary: #14b8a6;
        --danger: #ef4444; --success: #10b981; --bg: #f8fafc; --card-bg: #ffffff;
        --text-main: #334155; --text-muted: #64748b; --border: #e2e8f0;
        --nav-bg: #ffffff; --input-bg: #ffffff;
        --chat-bg: #ffffff; --chat-user: #0d9488; --chat-bot: #f1f5f9; --chat-text-bot: #334155;
    }
    [data-theme="dark"] {
        --primary: #2dd4bf; --primary-dark: #0d9488; --bg: #0f172a;
        --card-bg: #1e293b; --text-main: #f1f5f9; --text-muted: #94a3b8;
        --border: #334155; --nav-bg: #1e293b; --input-bg: #1e293b;
        --chat-bg: #1e293b; --chat-user: #0d9488; --chat-bot: #334155; --chat-text-bot: #f1f5f9;
    }
    * { box-sizing: border-box; transition: background 0.3s, border 0.3s; }
    body { background-color: var(--bg); font-family: 'Inter', sans-serif; color: var(--text-main); margin: 0; display: flex; flex-direction: column; min-height: 100vh; }
    .main-content { flex: 1; width: 100%; }
    
    /* Navigation */
    .nav { background: var(--nav-bg); border-bottom: 1px solid var(--border); padding: 1rem 0; position: sticky; top: 0; z-index: 50; }
    .nav-container { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }
    .nav-brand { font-size: 1.5rem; font-weight: 800; color: var(--primary); text-decoration: none; display: flex; align-items: center; gap: 8px; }
    .nav-links { display: flex; gap: 1rem; align-items: center; }
    .nav a { text-decoration: none; color: var(--text-muted); font-weight: 600; font-size: 0.95rem; }
    .nav a:hover { color: var(--primary); }
    
    /* Buttons */
    .btn { display: inline-flex; justify-content: center; align-items: center; padding: 0.75rem 1.25rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; border: none; font-size: 0.95rem; width: 100%; transition: all 0.2s; text-decoration: none; }
    .btn-auto { width: auto; }
    .btn-primary { background: var(--primary); color: white !important; }
    .btn-primary:hover { background: var(--primary-dark); transform: translateY(-1px); }
    .btn-outline { border: 1px solid var(--border); background: transparent; color: var(--text-main); }
    .btn-danger { color: var(--danger); background: transparent; border: 1px solid var(--danger); font-size: 0.85rem; padding: 0.4rem; }
    .btn-registered { color: var(--success); background: transparent; border: 2px solid var(--success); }
    .btn-registered:hover { background: rgba(16, 185, 129, 0.1); content: "Unregister"; }
    .btn-nav-primary { background: var(--primary); color: white !important; padding: 0.5rem 1rem; border-radius: 99px; }
    .btn-nav-secondary { border: 2px solid var(--border); background: transparent; color: var(--text-muted) !important; padding: 0.5rem 1rem; border-radius: 99px; }
    
    /* Layout */
    .container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 2rem; }
    .hero { background: linear-gradient(135deg, #115e59 0%, #0d9488 100%); padding: 4rem 1.5rem; text-align: center; color: white; margin-bottom: 3rem; }
    .hero h1 { margin: 0; font-size: 4rem; font-weight: 700; font-family: 'Dancing Script', cursive; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .hero p { font-size: 1.8rem; color: rgba(255, 255, 255, 0.9); margin-top: 1rem; max-width: 700px; margin-left: auto; margin-right: auto; font-weight: 400; font-family: 'Dancing Script', cursive; }

    /* Cards */
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 0.75rem; padding: 1.5rem; display: flex; flex-direction: column; position: relative; overflow: hidden; }
    .card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--primary); }
    .card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .card-title { margin: 0.5rem 0; font-size: 1.25rem; font-weight: 700; }
    .card-meta { margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); }
    
    /* Forms & Auth */
    .form-group { margin-bottom: 1rem; }
    .form-control { width: 100%; padding: 0.75rem; border: 1px solid var(--border); border-radius: 0.5rem; background: var(--input-bg); color: var(--text-main); font-family: inherit; }
    .form-control:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1); }
    label { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; display: block; }
    
    /* NEW AUTH STYLES */
    .auth-wrapper { display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 200px); padding: 2rem 1rem; }
    .auth-card { 
        width: 100%; max-width: 420px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 1rem; 
        padding: 2.5rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); 
        position: relative; overflow: hidden; 
    }
    .auth-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 6px; background: linear-gradient(to right, var(--primary), var(--secondary)); }
    .auth-header { text-align: center; margin-bottom: 2rem; }
    .auth-title { font-size: 1.8rem; font-weight: 800; color: var(--text-main); margin-bottom: 0.5rem; }
    .auth-subtitle { color: var(--text-muted); font-size: 0.95rem; }
    .auth-footer { text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid var(--border); font-size: 0.9rem; color: var(--text-muted); }
    .auth-footer a { color: var(--primary); font-weight: 600; text-decoration: none; transition: color 0.2s; }
    .auth-footer a:hover { text-decoration: underline; color: var(--primary-dark); }

    /* Admin Badge */
    .badge-admin { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; border: 1px solid #fcd34d; margin-left: 5px; }
    .badge-tag { background: var(--bg); padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid var(--border); }

    /* Chatbot Styles */
    .chat-widget { position: fixed; bottom: 20px; right: 20px; z-index: 1000; }
    .chat-btn { width: 60px; height: 60px; border-radius: 50%; background: var(--primary); color: white; border: none; font-size: 1.5rem; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .chat-win { position: absolute; bottom: 80px; right: 0; width: 300px; height: 400px; background: var(--chat-bg); border: 1px solid var(--border); border-radius: 12px; display: none; flex-direction: column; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
    .chat-head { background: var(--primary); color: white; padding: 10px 15px; font-weight: bold; display: flex; justify-content: space-between; }
    .chat-body { flex: 1; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
    .chat-msg { padding: 8px 12px; border-radius: 8px; max-width: 85%; font-size: 0.9rem; }
    .msg-bot { background: var(--chat-bot); color: var(--chat-text-bot); align-self: flex-start; }
    .msg-user { background: var(--chat-user); color: white; align-self: flex-end; }
    .chat-foot { padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 5px; background: var(--input-bg); }
    
    .alert { padding: 1rem; margin-bottom: 1rem; border-radius: 0.5rem; font-weight: 500; }
    .alert-error { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
    .alert-success { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
</style>
"""


SCRIPTS = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    // THEME LOGIC
    const btn = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const saved = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', saved);
    btn.textContent = saved === 'light' ? '🌙' : '☀️';
    btn.addEventListener('click', () => {
        const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        btn.textContent = next === 'light' ? '🌙' : '☀️';
    });

    // CHATBOT LOGIC
    const chatBtn = document.getElementById('chat-btn');
    const chatWin = document.getElementById('chat-win');
    const chatIn = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatBody = document.getElementById('chat-body');

    if(chatBtn){
        chatBtn.onclick = () => chatWin.style.display = chatWin.style.display === 'flex' ? 'none' : 'flex';
        document.getElementById('chat-close').onclick = () => chatWin.style.display = 'none';

        function send() {
            const txt = chatIn.value.trim();
            if(!txt) return;
            addMsg(txt, 'msg-user');
            chatIn.value = '';
            fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:txt})})
            .then(r=>r.json()).then(d=>addMsg(d.response, 'msg-bot'));
        }
        function addMsg(txt, cls) {
            const d = document.createElement('div');
            d.className = 'chat-msg ' + cls;
            d.textContent = txt;
            chatBody.appendChild(d);
            chatBody.scrollTop = chatBody.scrollHeight;
        }
        chatSend.onclick = send;
        chatIn.onkeypress = (e) => { if(e.key === 'Enter') send(); }
    }
});
</script>
"""


def render_page(content, hero_html=""):
    nav_links = ""
    if 'username' in session:
        role_badge = '<span class="badge-admin">ADMIN</span>' if session.get('role') == 'admin' else ''
        nav_links += f"""<span style="color:var(--text-muted); font-size:0.9rem;">Hi, <strong>{session['username']}</strong>{role_badge}</span>
        <a href="/">Events</a><a href="/clubs">Clubs</a>"""
        if session.get('role') == 'admin':
            nav_links += """<a href="/create_event" class="btn-nav-primary">Host Event</a>"""
        nav_links += '<a href="/logout" style="color:var(--danger)">Logout</a>'
    else:
        nav_links = """<a href="/">Events</a><a href="/clubs">Clubs</a><a href="/login" class="btn-nav-secondary">Log In</a><a href="/signup" class="btn-nav-primary">Sign Up</a>"""

    msgs_html = ""
    messages = get_flashed_messages(with_categories=True)
    if messages:
        for cat, msg in messages:
            c = 'error' if cat == 'error' else 'success'
            msgs_html += f'<div class="alert alert-{c}">{msg}</div>'

    logo_svg = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>"""

    return f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>ClubHub</title>{STYLES}</head>
    <body>
        <nav class="nav"><div class="nav-container"><a href="/" class="nav-brand">{logo_svg} ClubHub</a><div class="nav-links">{nav_links}<button id="theme-toggle" style="background:none;border:none;cursor:pointer;font-size:1.2rem;">🌙</button></div></div></nav>
        <div class="main-content">{hero_html}<div class="container" style="margin-top:2rem;">{msgs_html}</div>{content}</div>
        <div style="text-align:center; padding:3rem; color:var(--text-muted);">&copy; 2025 ClubHub</div>
        
        <div class="chat-widget">
            <button id="chat-btn" class="chat-btn">💬</button>
            <div id="chat-win" class="chat-win">
                <div class="chat-head"><span>ClubHub Bot</span><span id="chat-close" style="cursor:pointer;">×</span></div>
                <div id="chat-body" class="chat-body"><div class="chat-msg msg-bot">Hi! Ask me about events or clubs.</div></div>
                <div class="chat-foot"><input id="chat-input" class="form-control" style="margin:0" placeholder="Type..."><button id="chat-send" class="btn-primary" style="padding:0 15px; border-radius:5px;">➤</button></div>
            </div>
        </div>
        {SCRIPTS}
    </body></html>
    """



@app.route('/')
def home():
    user = session.get('username')
    role = session.get('role')
    events = sorted(events_table.all(), key=lambda x: x.get('date', '9999'))
    
    for e in events:
        if 'id' not in e:
            uid = str(uuid.uuid4())
            events_table.update({'id': uid}, Query().title == e['title'])
            e['id'] = uid

    my_regs = [r['event_id'] for r in registrations_table.search(Query().username == user)] if user else []
    
    hero = """<div class="hero"><div class="container"><h1>Connect. Participate. Lead.</h1><p>Your hub for campus events and clubs.</p></div></div>"""
    
    html = '<div class="container"><div class="grid">'
    if not events:
        html += '<p>No events found.</p>'
    
    for e in events:
        p_count = registrations_table.count(Query().event_id == e['id'])
        if not user:
            btn = '<a href="/login" class="btn btn-outline">Login to Register</a>'
        elif e['id'] in my_regs:
            btn = f"""<form action="/unregister/{e['id']}" method="POST"><button class="btn btn-registered">✓ Registered</button></form>"""
        else:
            btn = f"""<form action="/register_event/{e['id']}" method="POST"><button class="btn btn-primary">Register Now</button></form>"""
        
        del_btn = ""
        if role == 'admin':
            del_btn = f"""<form action="/delete_event/{e['id']}" method="POST" style="margin-top:10px;"><button class="btn btn-danger">Delete Event</button></form>"""

        html += f"""
        <div class="card">
            <h3 class="card-title">{e['title']}</h3>
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <span class="badge-tag">{e.get('type','Event')}</span>
                <small style="color:var(--primary); font-weight:bold;">{e['club_name']}</small>
            </div>
            <p style="color:var(--text-muted); flex-grow:1;">{e['description']}</p>
            <div style="margin-bottom:0.5rem; font-size:0.9rem; font-weight:600; color:var(--text-main);">
                👥 {p_count} Participant{'s' if p_count != 1 else ''}
            </div>
            <div class="card-meta"><span>📅 {e['date']}</span><span>📍 {e['location']}</span></div>
            <div style="margin-top:1.5rem; display:flex; flex-direction:column; gap:0.5rem;">{btn}{del_btn}</div>
        </div>"""
    
    html += '</div></div>'
    return render_page(html, hero)

@app.route('/clubs')
def clubs():
    role = session.get('role')
    create_btn = '<a href="/register_club" class="btn btn-outline btn-auto">+ Register New Club</a>' if role == 'admin' else ''
    html = f"""<div class="container"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem;"><h2>Clubs</h2>{create_btn}</div><div class="grid">"""
    for c in clubs_table.all():
        del_btn = ""
        if role == 'admin':
            del_btn = f"""<div style="margin-top:1rem; border-top:1px solid var(--border); padding-top:1rem;"><form action="/delete_club/{c['name']}" method="POST" onsubmit="return confirm('Delete club?');"><button class="btn btn-danger">Delete Club</button></form></div>"""
        html += f"""<div class="card"><h3 class="card-title">{c['name']}</h3><p>{c['description']}</p><small>Leader: {c['leader']}</small>{del_btn}</div>"""
    return render_page(html + '</div></div>')

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.get_json().get('message', '').lower()
    resp = "I can help with events, clubs, or registration."
    if 'register' in msg: resp = "Log in, find an event, and click 'Register Now'."
    elif 'host' in msg or 'create' in msg: resp = "Log in as Admin and click 'Host Event'."
    elif 'club' in msg: resp = "Check the 'Clubs' page to join or start one."
    return jsonify({'response': resp})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        results = users_table.search(Query().username == request.form['username'])
        if results:
            u = results[0]
            if check_password_hash(u['password'], request.form['password']):
                session['username'] = u['username']
                session['role'] = u.get('role', 'student') 
                return redirect('/')
        flash('Invalid credentials', 'error')
    
    return render_page("""
    <div class="auth-wrapper">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-title">Welcome Back</div>
                <div class="auth-subtitle">Sign in to your ClubHub account</div>
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input name="username" class="form-control" required placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="••••••••">
                </div>
                <button class="btn btn-primary" style="margin-top:1rem; padding:0.8rem;">Log In</button>
            </form>
            <div class="auth-footer">
                Don't have an account? <a href="/signup">Sign up</a>
            </div>
        </div>
    </div>
    """)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if users_table.search(Query().username == request.form['username']):
            flash('Username taken', 'error')
        else:
            users_table.insert({
                'username': request.form['username'], 
                'password': generate_password_hash(request.form['password']),
                'role': request.form['role']
            })
            flash('Account created', 'success')
            return redirect('/login')
    
 
    return render_page("""
    <div class="auth-wrapper">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-title">Create Account</div>
                <div class="auth-subtitle">Join the ClubHub community today</div>
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input name="username" class="form-control" required placeholder="Choose a username">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="Create a password">
                </div>
                <div class="form-group">
                    <label>I am a...</label>
                    <select name="role" class="form-control" style="height:45px;">
                        <option value="student">Student (Browse & Register)</option>
                        <option value="admin">Admin (Host Events & Clubs)</option>
                    </select>
                </div>
                <button class="btn btn-primary" style="margin-top:1rem; padding:0.8rem;">Create Account</button>
            </form>
            <div class="auth-footer">
                Already have an account? <a href="/login">Log in</a>
            </div>
        </div>
    </div>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if session.get('role') != 'admin': return redirect('/')
    if request.method == 'POST':
        events_table.insert({
            'id': str(uuid.uuid4()),
            'title': request.form['title'], 'club_name': request.form['club_name'],
            'type': request.form['type'], 'date': request.form['date'],
            'location': request.form['location'], 'description': request.form['description'],
            'created_by': session['username']
        })
        flash('Event Created!', 'success')
        return redirect('/')
    clubs = clubs_table.all()
    if not clubs: return render_page('<div class="container">Please register a club first.</div>')
    opts = "".join([f"<option value='{c['name']}'>{c['name']}</option>" for c in clubs])
    return render_page(f"""
    <div class="auth-wrapper"><div class="auth-card">
    <h2 style="text-align:center; margin-bottom:1.5rem;">Host Event</h2><form method="POST">
    <div class="form-group"><label>Title</label><input name="title" class="form-control" required></div>
    <div class="form-group"><label>Club</label><select name="club_name" class="form-control">{opts}</select></div>
    <div class="form-group"><label>Type</label><select name="type" class="form-control"><option>Competition</option><option>Comedy</option><option>Workshop</option><option>Social</option></select></div>
    <div class="form-group"><label>Date</label><input type="date" name="date" class="form-control" required></div>
    <div class="form-group"><label>Location</label><input name="location" class="form-control" required></div>
    <div class="form-group"><label>Description</label><textarea name="description" class="form-control"></textarea></div>
    <button class="btn btn-primary" style="margin-top:1rem;">Publish</button></form></div></div>
    """)

@app.route('/register_club', methods=['GET', 'POST'])
def register_club():
    if session.get('role') != 'admin': return redirect('/')
    if request.method == 'POST':
        if clubs_table.search(Query().name == request.form['name']):
            flash('Club exists', 'error')
        else:
            clubs_table.insert({
                'name': request.form['name'], 'description': request.form['description'],
                'leader': request.form['leader'], 'founded': str(datetime.date.today()),
                'created_by': session['username']
            })
            return redirect('/clubs')
    return render_page("""
    <div class="auth-wrapper"><div class="auth-card">
    <h2 style="text-align:center; margin-bottom:1.5rem;">Register Club</h2><form method="POST">
    <div class="form-group"><label>Club Name</label><input name="name" class="form-control" required></div>
    <div class="form-group"><label>Description</label><textarea name="description" class="form-control"></textarea></div>
    <div class="form-group"><label>Leader</label><input name="leader" class="form-control" required></div>
    <button class="btn btn-primary" style="margin-top:1rem;">Register</button></form></div></div>
    """)

@app.route('/delete_event/<eid>', methods=['POST'])
def delete_event(eid):
    if session.get('role') == 'admin':
        events_table.remove(Query().id == eid)
        flash('Deleted', 'success')
    return redirect('/')

@app.route('/delete_club/<name>', methods=['POST'])
def delete_club(name):
    if session.get('role') == 'admin':
        clubs_table.remove(Query().name == name)
        events_table.remove(Query().club_name == name)
        flash('Club deleted', 'success')
    return redirect('/clubs')

@app.route('/register_event/<eid>', methods=['POST'])
def reg_event(eid):
    if 'username' not in session: return redirect('/login')
    if not registrations_table.search((Query().event_id == eid) & (Query().username == session['username'])):
        registrations_table.insert({'event_id': eid, 'username': session['username']})
    return redirect('/')

@app.route('/unregister/<eid>', methods=['POST'])
def unreg(eid):
    registrations_table.remove((Query().event_id == eid) & (Query().username == session.get('username')))
    return redirect('/')

@app.route('/reset_db')
def reset_db():
    db.drop_tables()
    initialize_system()
    session.clear()
    flash("Database wiped.", "success")
    return redirect('/login')

if __name__ == '__main__':
    initialize_system()
    app.run(debug=True)