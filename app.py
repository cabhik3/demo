from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json

app = Flask(__name__)
app.secret_key = 'chakracoach_secret_key'

USER_DB = 'users.txt'
SCORES_FILE = 'user_scores.json'

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    users = {}
    with open(USER_DB, 'r') as f:
        for line in f:
            username, password = line.strip().split(',')
            users[username] = password
    return users

def save_user(username, password):
    with open(USER_DB, 'a') as f:
        f.write(f"{username},{password}\n")

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return {}
    with open(SCORES_FILE, 'r') as f:
        return json.load(f)

def get_user_scores(username):
    scores = load_scores()
    return scores.get(username, [50, 50, 50, 50, 50, 50])

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return "Invalid login"

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    users = load_users()
    if username in users:
        return "User already exists"
    save_user(username, password)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/section/<category>/<topic>')
def show_section(category, topic):
    with open('content.json') as f:
        data = json.load(f)
    content = data.get(category, {}).get(topic, "Content not available for this section.")
    return render_template('section.html', category=category, topic=topic, content=content)

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/running', methods=['GET', 'POST'])
def running():
    advice = None
    if request.method == 'POST':
        try:
            time = float(request.form['time'])
            if time < 12:
                advice = "You're doing great! Focus on sprint starts and explosive strength."
            elif time < 15:
                advice = "Good job! Improve form and do interval training."
            else:
                advice = "Let's build up your stamina with consistent short runs and strength work."
        except ValueError:
            advice = "Please enter a valid number."
    return render_template('running.html', advice=advice)

@app.route('/graph')
def graph():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('graph.html', username=session['username'])

@app.route('/api/graph-data')
def graph_data():
    if 'username' not in session:
        return jsonify([])
    scores = get_user_scores(session['username'])
    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True)
