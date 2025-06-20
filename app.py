from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'test_secret_key_123'

def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Table des tâches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Créer un utilisateur test
    password_hash = hashlib.sha256('password123'.encode()).hexdigest()
    cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', 
                   ('testuser', password_hash))
    
    conn.commit()
    conn.close()

def login_required(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """Hash un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Vérifie les identifiants utilisateur"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', 
                   (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def get_user_tasks(user_id):
    """Récupère les tâches d'un utilisateur"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, completed FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return [{'id': t[0], 'title': t[1], 'description': t[2], 'completed': bool(t[3])} for t in tasks]

def add_task(title, description, user_id):
    """Ajoute une nouvelle tâche"""
    if not title or not title.strip():
        return False
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)', 
                   (title.strip(), description, user_id))
    conn.commit()
    conn.close()
    return True

def update_task_status(task_id, user_id):
    """Met à jour le statut d'une tâche"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = NOT completed WHERE id = ? AND user_id = ?', 
                   (task_id, user_id))
    conn.commit()
    conn.close()

def delete_task(task_id, user_id):
    """Supprime une tâche"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_id = verify_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = get_user_tasks(session['user_id'])
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task_route():
    title = request.form['title']
    description = request.form.get('description', '')
    
    if add_task(title, description, session['user_id']):
        flash('Tâche ajoutée avec succès!', 'success')
    else:
        flash('Erreur: le titre est requis', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/toggle_task/<int:task_id>')
@login_required
def toggle_task(task_id):
    update_task_status(task_id, session['user_id'])
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task_route(task_id):
    delete_task(task_id, session['user_id'])
    flash('Tâche supprimée', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)