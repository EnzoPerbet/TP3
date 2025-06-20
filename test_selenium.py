import pytest
import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from app import app, init_db

class TestServer:
    """Serveur de test pour les tests Selenium"""
    
    def __init__(self):
        self.server_thread = None
        self.app = app
        self.app.config['TESTING'] = True
        
    def start(self):
        """Démarre le serveur de test"""
        # Nettoyer et initialiser la DB
        if os.path.exists('app.db'):
            os.unlink('app.db')
        init_db()
        
        # Démarrer le serveur dans un thread séparé
        self.server_thread = threading.Thread(
            target=lambda: self.app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(2)  # Attendre que le serveur démarre
    
    def stop(self):
        """Arrête le serveur de test"""
        if os.path.exists('app.db'):
            os.unlink('app.db')

@pytest.fixture(scope="session")
def test_server():
    """Fixture pour démarrer/arrêter le serveur de test"""
    server = TestServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture
def driver():
    """Fixture pour le driver Selenium"""
    options = Options()
    options.add_argument('--headless')  # Mode sans interface
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

class TestSeleniumUI:
    """Tests fonctionnels avec Selenium"""
    
    BASE_URL = "http://127.0.0.1:5000"
    
    def test_home_page_elements(self, driver, test_server):
        """Test des éléments de la page d'accueil"""
        driver.get(self.BASE_URL)
        
        # Vérifier le titre
        assert "Task Manager" in driver.title
        
        # Vérifier les éléments principaux
        home_div = driver.find_element(By.ID, "home-page")
        assert home_div.is_displayed()
        
        # Vérifier le titre principal
        h1 = driver.find_element(By.TAG_NAME, "h1")
        assert "Bienvenue sur Task Manager" in h1.text
        
        # Vérifier le lien de connexion
        login_link = driver.find_element(By.LINK_TEXT, "Se connecter pour commencer")
        assert login_link.is_displayed()
        
        # Vérifier les informations de test
        assert "testuser" in driver.page_source
        assert "password123" in driver.page_source
    
    def test_navigation_links(self, driver, test_server):
        """Test des liens de navigation"""
        driver.get(self.BASE_URL)
        
        # Cliquer sur le lien de connexion dans la navigation
        nav_login_link = driver.find_element(By.LINK_TEXT, "Connexion")
        nav_login_link.click()
        
        # Vérifier qu'on est sur la page de connexion
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-page"))
        )
        
        # Retourner à l'accueil
        home_link = driver.find_element(By.LINK_TEXT, "Accueil")
        home_link.click()
        
        # Vérifier qu'on est de retour à l'accueil
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "home-page"))
        )
    
    def test_login_form_elements(self, driver, test_server):
        """Test des éléments du formulaire de connexion"""
        driver.get(f"{self.BASE_URL}/login")
        
        # Vérifier les éléments du formulaire
        login_form = driver.find_element(By.ID, "login-form")
        assert login_form.is_displayed()
        
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_btn = driver.find_element(By.ID, "login-btn")
        
        assert username_input.is_displayed()
        assert password_input.is_displayed()
        assert login_btn.is_displayed()
        
        # Vérifier les attributs
        assert username_input.get_attribute("type") == "text"
        assert password_input.get_attribute("type") == "password"
        assert username_input.get_attribute("required") == "true"
        assert password_input.get_attribute("required") == "true"
    
    def test_login_success(self, driver, test_server):
        """Test de connexion réussie"""
        driver.get(f"{self.BASE_URL}/login")
        
        # Remplir le formulaire
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_btn = driver.find_element(By.ID, "login-btn")
        
        username_input.send_keys("testuser")
        password_input.send_keys("password123")
        login_btn.click()
        
        # Vérifier la redirection vers le dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard-page"))
        )
        
        # Vérifier le message de succès
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Connexion réussie!" in success_alert.text
        
        # Vérifier que l'utilisateur est connecté (navigation)
        assert "testuser" in driver.page_source
        assert "Déconnexion" in driver.page_source
    
    def test_login_failure(self, driver, test_server):
        """Test de connexion échouée"""
        driver.get(f"{self.BASE_URL}/login")
        
        # Remplir avec de mauvais identifiants
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_btn = driver.find_element(By.ID, "login-btn")
        
        username_input.send_keys("wronguser")
        password_input.send_keys("wrongpassword")
        login_btn.click()
        
        # Vérifier qu'on reste sur la page de connexion
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-page"))
        )
        
        # Vérifier le message d'erreur
        error_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-error"))
        )
        assert "Identifiants incorrects" in error_alert.text
    
    def test_dashboard_elements(self, driver, test_server):
        """Test des éléments du dashboard"""
        # Se connecter d'abord
        self._login(driver)
        
        # Vérifier les éléments du dashboard
        dashboard_div = driver.find_element(By.ID, "dashboard-page")
        assert dashboard_div.is_displayed()
        
        # Vérifier le formulaire d'ajout
        add_form = driver.find_element(By.ID, "add-task-form")
        assert add_form.is_displayed()
        
        title_input = driver.find_element(By.ID, "title")
        description_input = driver.find_element(By.ID, "description")
        add_btn = driver.find_element(By.ID, "add-task-btn")
        
        assert title_input.is_displayed()
        assert description_input.is_displayed()
        assert add_btn.is_displayed()
        
        # Vérifier qu'il n'y a pas de tâches initialement
        no_tasks_div = driver.find_element(By.ID, "no-tasks")
        assert no_tasks_div.is_displayed()
        assert "Aucune tâche pour le moment" in no_tasks_div.text
    
    def test_add_task_functionality(self, driver, test_server):
        """Test de l'ajout de tâches"""
        # Se connecter
        self._login(driver)
        
        # Ajouter une tâche
        title_input = driver.find_element(By.ID, "title")
        description_input = driver.find_element(By.ID, "description")
        add_btn = driver.find_element(By.ID, "add-task-btn")
        
        title_input.send_keys("Tâche de test Selenium")
        description_input.send_keys("Description de test")
        add_btn.click()
        
        # Vérifier le message de succès
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Tâche ajoutée avec succès!" in success_alert.text
        
        # Vérifier que la tâche apparaît
        tasks_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tasks-list"))
        )
        assert "Tâche de test Selenium" in tasks_list.text
        assert "Description de test" in tasks_list.text
        
        # Vérifier que le div "no-tasks" a disparu
        try:
            driver.find_element(By.ID, "no-tasks")
            assert False, "Le div 'no-tasks' devrait avoir disparu"
        except:
            pass  # C'est ce qu'on attend
    
    def test_task_completion_toggle(self, driver, test_server):
        """Test du basculement de l'état d'une tâche"""
        # Se connecter et ajouter une tâche
        self._login(driver)
        self._add_task(driver, "Tâche à compléter", "Description")
        
        # Trouver le bouton de basculement
        toggle_btn = driver.find_element(By.ID, "toggle-1")
        assert "Marquer comme terminée" in toggle_btn.text
        
        # Marquer comme terminée
        toggle_btn.click()
        
        # Vérifier que la tâche est marquée comme terminée
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "toggle-1"), "Marquer comme non terminée")
        )
        
        # Vérifier l'indicateur visuel
        task_div = driver.find_element(By.CSS_SELECTOR, "[data-task-id='1']")
        assert "completed" in task_div.get_attribute("class")
        assert "[TERMINÉE]" in task_div.text
    
    def test_task_deletion(self, driver, test_server):
        """Test de la suppression de tâches"""
        # Se connecter et ajouter une tâche
        self._login(driver)
        self._add_task(driver, "Tâche à supprimer", "Description")
        
        # Vérifier que la tâche existe
        tasks_list = driver.find_element(By.ID, "tasks-list")
        assert "Tâche à supprimer" in tasks_list.text
        
        # Supprimer la tâche (gérer l'alerte de confirmation)
        delete_btn = driver.find_element(By.ID, "delete-1")
        driver.execute_script("arguments[0].click();", delete_btn)
        
        # Gérer l'alerte JavaScript
        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.accept()
        except TimeoutException:
            # Si pas d'alerte, continuer
            pass
        
        # Vérifier que la tâche a été supprimée
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "no-tasks"))
        )
        
        # Vérifier le message de succès
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Tâche supprimée" in success_alert.text
    
    def test_multiple_tasks_workflow(self, driver, test_server):
        """Test d'un workflow complet avec plusieurs tâches"""
        # Se connecter
        self._login(driver)
        
        # Ajouter plusieurs tâches
        tasks = [
            ("Tâche 1", "Description 1"),
            ("Tâche 2", "Description 2"),
            ("Tâche 3", "Description 3")
        ]
        
        for title, description in tasks:
            self._add_task(driver, title, description)
        
        # Vérifier que toutes les tâches sont présentes
        tasks_list = driver.find_element(By.ID, "tasks-list")
        for title, _ in tasks:
            assert title in tasks_list.text
        
        # Vérifier le compteur de tâches
        assert "Mes tâches (3)" in driver.page_source
        
        # Marquer la première tâche comme terminée
        toggle_btn = driver.find_element(By.ID, "toggle-1")
        toggle_btn.click()
        
        # Vérifier que seule la première tâche est terminée
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-task-id='1'].completed"))
        )
        
        # Vérifier que les autres ne sont pas terminées
        task2 = driver.find_element(By.CSS_SELECTOR, "[data-task-id='2']")
        task3 = driver.find_element(By.CSS_SELECTOR, "[data-task-id='3']")
        assert "completed" not in task2.get_attribute("class")
        assert "completed" not in task3.get_attribute("class")
    
    def test_logout_functionality(self, driver, test_server):
        """Test de la déconnexion"""
        # Se connecter
        self._login(driver)
        
        # Vérifier qu'on est connecté
        assert "testuser" in driver.page_source
        assert "Déconnexion" in driver.page_source
        
        # Se déconnecter
        logout_link = driver.find_element(By.LINK_TEXT, "Déconnexion (testuser)")
        logout_link.click()
        
        # Vérifier la redirection et le message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "home-page"))
        )
        
        success_alert = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        assert "Déconnexion réussie" in success_alert.text
        
        # Vérifier qu'on ne peut plus accéder au dashboard
        driver.get(f"{self.BASE_URL}/dashboard")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-page"))
        )
    
    def _login(self, driver):
        """Méthode helper pour se connecter"""
        driver.get(f"{self.BASE_URL}/login")
        
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_btn = driver.find_element(By.ID, "login-btn")
        
        username_input.send_keys("testuser")
        password_input.send_keys("password123")
        login_btn.click()
        
        # Attendre d'être sur le dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard-page"))
        )
    
    def _add_task(self, driver, title, description):
        """Méthode helper pour ajouter une tâche"""
        title_input = driver.find_element(By.ID, "title")
        description_input = driver.find_element(By.ID, "description")
        add_btn = driver.find_element(By.ID, "add-task-btn")
        
        title_input.clear()
        description_input.clear()
        
        title_input.send_keys(title)
        description_input.send_keys(description)
        add_btn.click()
        
        # Attendre le message de succès
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )