import pytest
import tempfile
import os
from app import app, init_db, hash_password, verify_user, add_task, get_user_tasks, update_task_status, delete_task
import sqlite3

@pytest.fixture
def client():
    """Fixture pour créer un client de test"""
    # Créer une base de données temporaire
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    # Modifier la fonction init_db pour utiliser une DB temporaire
    original_db_name = 'app.db'
    temp_db_name = 'test_app.db'
    
    with app.test_client() as client:
        with app.app_context():
            # Remplacer temporairement le nom de la DB
            import app as app_module
            original_connect = sqlite3.connect
            
            def mock_connect(db_name):
                if db_name == original_db_name:
                    return original_connect(temp_db_name)
                return original_connect(db_name)
            
            sqlite3.connect = mock_connect
            init_db()
            
            yield client
            
            # Nettoyer
            sqlite3.connect = original_connect
            if os.path.exists(temp_db_name):
                os.unlink(temp_db_name)
    
    os.close(db_fd)
    if os.path.exists(app.config['DATABASE']):
        os.unlink(app.config['DATABASE'])

class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""
    
    def test_hash_password(self):
        """Test du hashage de mot de passe"""
        password = "test123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) == 64  # SHA256 produit 64 caractères hex
        assert hashed != password  # Le hash ne doit pas être le mot de passe en clair
        
        # Le même mot de passe doit produire le même hash
        assert hash_password(password) == hashed
    
    def test_hash_password_different_inputs(self):
        """Test que des mots de passe différents produisent des hashes différents"""
        password1 = "password123"
        password2 = "password456"
        
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        
        assert hash1 != hash2

class TestDatabaseFunctions:
    """Tests pour les fonctions de base de données"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.test_db = 'test_app.db'
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
        
        # Patcher sqlite3.connect pour utiliser la DB de test
        self.original_connect = sqlite3.connect
        sqlite3.connect = lambda db: self.original_connect(self.test_db if db == 'app.db' else db)
        
        init_db()
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        sqlite3.connect = self.original_connect
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
    
    def test_verify_user_success(self):
        """Test de vérification d'utilisateur valide"""
        user_id = verify_user('testuser', 'password123')
        assert user_id is not None
        assert isinstance(user_id, int)
    
    def test_verify_user_wrong_password(self):
        """Test de vérification avec mauvais mot de passe"""
        user_id = verify_user('testuser', 'wrongpassword')
        assert user_id is None
    
    def test_verify_user_wrong_username(self):
        """Test de vérification avec mauvais nom d'utilisateur"""
        user_id = verify_user('wronguser', 'password123')
        assert user_id is None
    
    def test_add_task_success(self):
        """Test d'ajout de tâche réussi"""
        user_id = verify_user('testuser', 'password123')
        result = add_task('Test Task', 'Test Description', user_id)
        assert result is True
        
        # Vérifier que la tâche a été ajoutée
        tasks = get_user_tasks(user_id)
        assert len(tasks) == 1
        assert tasks[0]['title'] == 'Test Task'
        assert tasks[0]['description'] == 'Test Description'
        assert tasks[0]['completed'] is False
    
    def test_add_task_empty_title(self):
        """Test d'ajout de tâche avec titre vide"""
        user_id = verify_user('testuser', 'password123')
        result = add_task('', 'Description', user_id)
        assert result is False
        
        result = add_task('   ', 'Description', user_id)
        assert result is False
        
        result = add_task(None, 'Description', user_id)
        assert result is False
    
    def test_get_user_tasks_empty(self):
        """Test de récupération des tâches pour un utilisateur sans tâches"""
        user_id = verify_user('testuser', 'password123')
        tasks = get_user_tasks(user_id)
        assert tasks == []
    
    def test_get_user_tasks_multiple(self):
        """Test de récupération de multiples tâches"""
        user_id = verify_user('testuser', 'password123')
        
        add_task('Task 1', 'Description 1', user_id)
        add_task('Task 2', 'Description 2', user_id)
        add_task('Task 3', '', user_id)
        
        tasks = get_user_tasks(user_id)
        assert len(tasks) == 3
        
        titles = [task['title'] for task in tasks]
        assert 'Task 1' in titles
        assert 'Task 2' in titles
        assert 'Task 3' in titles
    
    def test_update_task_status(self):
        """Test de mise à jour du statut d'une tâche"""
        user_id = verify_user('testuser', 'password123')
        add_task('Test Task', 'Description', user_id)
        
        tasks = get_user_tasks(user_id)
        task_id = tasks[0]['id']
        
        # Initialement, la tâche n'est pas terminée
        assert tasks[0]['completed'] is False
        
        # Marquer comme terminée
        update_task_status(task_id, user_id)
        tasks = get_user_tasks(user_id)
        assert tasks[0]['completed'] is True
        
        # Marquer comme non terminée
        update_task_status(task_id, user_id)
        tasks = get_user_tasks(user_id)
        assert tasks[0]['completed'] is False
    
    def test_delete_task(self):
        """Test de suppression de tâche"""
        user_id = verify_user('testuser', 'password123')
        add_task('Task to delete', 'Description', user_id)
        
        tasks = get_user_tasks(user_id)
        assert len(tasks) == 1
        task_id = tasks[0]['id']
        
        delete_task(task_id, user_id)
        
        tasks = get_user_tasks(user_id)
        assert len(tasks) == 0

class TestRoutes:
    """Tests pour les routes de l'application"""
    
    def test_index_route(self, client):
        """Test de la page d'accueil"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Bienvenue sur Task Manager' in response.data
        assert b'home-page' in response.data
    
    def test_login_get(self, client):
        """Test de la page de connexion (GET)"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Connexion' in response.data
        assert b'login-form' in response.data
    
    def test_login_post_success(self, client):
        """Test de connexion réussie"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Connexion reussie!' in response.data
        assert b'dashboard-page' in response.data
    
    def test_login_post_failure(self, client):
        """Test de connexion échouée"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Identifiants incorrects' in response.data
    
    def test_dashboard_without_login(self, client):
        """Test d'accès au dashboard sans connexion"""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirection vers login
    
    def test_dashboard_with_login(self, client):
        """Test d'accès au dashboard avec connexion"""
        # Se connecter d'abord
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard - Mes Taches' in response.data
        assert b'Ajouter une nouvelle tache' in response.data
    
    def test_add_task_route(self, client):
        """Test d'ajout de tâche via la route"""
        # Se connecter
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Ajouter une tâche
        response = client.post('/add_task', data={
            'title': 'Test Task',
            'description': 'Test Description'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Tache ajoutee avec succes!' in response.data
        assert b'Test Task' in response.data
    
    def test_logout(self, client):
        """Test de déconnexion"""
        # Se connecter
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Se déconnecter
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Deconnexion reussie' in response.data
        
        # Vérifier qu'on ne peut plus accéder au dashboard
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirection vers login