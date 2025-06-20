#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du projet localement
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f" {description} - SUCCÈS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f" {description} - ÉCHEC")
        print("Error:", e.stderr)
        return False

def setup_environment():
    """Configure l'environnement de test"""
    print("Configuration de l'environnement...")
    
    # Créer le dossier reports s'il n'existe pas
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Vérifier les dépendances
    try:
        import flask, pytest, selenium
        print(" Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f" Dépendance manquante: {e}")
        print("Installez les dépendances avec: pip install -r requirements.txt")
        return False

def run_unit_tests():
    """Exécute les tests unitaires"""
    command = "python -m pytest test_app.py -v --html=reports/unit-tests-report.html --self-contained-html --cov=app --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml"
    return run_command(command, "Tests unitaires avec couverture de code")

def run_selenium_tests():
    """Exécute les tests Selenium"""
    # Vérifier si ChromeDriver est disponible
    try:
        subprocess.run(["chromedriver", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(" ChromeDriver non trouvé, installation automatique...")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            ChromeDriverManager().install()
        except ImportError:
            print(" webdriver-manager non installé. Ajoutez-le à requirements.txt")
            return False
    
    command = "python -m pytest test_selenium.py -v --html=reports/selenium-tests-report.html --self-contained-html"
    return run_command(command, "Tests fonctionnels Selenium")

def generate_combined_report():
    """Génère un rapport combiné"""
    report_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Rapport de Tests - Task Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; border-bottom: 2px solid #007bff; }
        h2 { color: #007bff; margin-top: 30px; }
        .report-link { 
            display: inline-block; 
            margin: 10px; 
            padding: 10px 20px; 
            background: #007bff; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
        }
        .report-link:hover { background: #0056b3; }
        .info { background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Rapport de Tests - Task Manager</h1>
    
    <div class="info">
        <strong>Application:</strong> Task Manager (Flask + SQLite)<br>
        <strong>Tests exécutés:</strong> Tests unitaires + Tests fonctionnels Selenium<br>
        <strong>Date:</strong> {date}
    </div>
    
    <h2>Rapports de Tests</h2>
    <a href="unit-tests-report.html" class="report-link">Tests Unitaires</a>
    <a href="selenium-tests-report.html" class="report-link">Tests Selenium</a>
    <a href="coverage-html/index.html" class="report-link">Couverture de Code</a>
    
    <h2>Résumé</h2>
    <ul>
        <li><strong>Tests unitaires:</strong> Validation des fonctions, routes et logique métier</li>
        <li><strong>Tests Selenium:</strong> Validation de l'interface utilisateur et des workflows</li>
        <li><strong>Couverture de code:</strong> Analyse de la couverture des tests</li>
    </ul>
    
    <h2>Pipeline CI/CD</h2>
    <p>Ce projet inclut un pipeline GitHub Actions qui:</p>
    <ul>
        <li>Récupère le code source (Loading)</li>
        <li>Installe les dépendances (Build)</li>
        <li>Exécute les tests unitaires avec Pytest</li>
        <li>Exécute les tests fonctionnels avec Selenium</li>
        <li>Génère des rapports HTML pour chaque type de test</li>
        <li>Déploie l'application si tous les tests passent</li>
        <li>Publie les rapports sur GitHub Pages</li>
    </ul>
</body>
</html>
    """.format(date=subprocess.run(["date"], capture_output=True, text=True).stdout.strip())
    
    with open("reports/index.html", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return True

def main():
    """Fonction principale"""
    print("LANCEMENT DES TESTS DU PROJET")
    
    if not setup_environment():
        print(" Erreur d'installation des dépendances. Abort.")
        sys.exit(1)
    
    success_unit = run_unit_tests()
    success_selenium = run_selenium_tests()
    
    if success_unit and success_selenium:
        print("\n TOUS LES TESTS ONT RÉUSSI")
    else:
        print("\n CERTAINS TESTS ONT ÉCHOUÉ")
    
    if generate_combined_report():
        report_path = Path("reports/index.html").resolve().as_uri()
        print(f"\nRapport généré ici : {report_path}")
        webbrowser.open(report_path)
    else:
        print(" Échec de la génération du rapport")
    
    # Retourne un code d'erreur si des tests ont échoué
    if not (success_unit and success_selenium):
        sys.exit(2)

if __name__ == "__main__":
    main()
