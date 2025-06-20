import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def test_division():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("http://localhost:5000")

    driver.find_element(By.NAME, "a").send_keys("10")
    driver.find_element(By.NAME, "b").send_keys("2")

    operation_select = driver.find_element(By.NAME, "operation")
    for option in operation_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == "division":
            option.click()
            break

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(1)

    assert "Résultat : 5.0" in driver.page_source

    driver.quit()

def test_division_par_zero():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("http://localhost:5000")

    driver.find_element(By.NAME, "a").send_keys("10")
    driver.find_element(By.NAME, "b").send_keys("0")

    operation_select = driver.find_element(By.NAME, "operation")
    for option in operation_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == "division":
            option.click()
            break

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(1)

    assert "Erreur : Division par zéro impossible" in driver.page_source

    driver.quit()


if __name__ == "__main__":
    test_division()
    print("Test division OK")
    test_division_par_zero()
    print("Test division par zéro OK")
