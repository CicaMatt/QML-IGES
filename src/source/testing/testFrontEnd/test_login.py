import hashlib

from cryptography.fernet import Fernet
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy_utils import database_exists, create_database

from src import app
from src import db
from src.source.model.models import User



class TestLogin():
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.vars = {}
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@127.0.0.1/quantumknn_db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            with app.app_context():
                create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        with app.app_context():
            password = "Password123"
            password = hashlib.sha512(password.encode()).hexdigest()
            utente = User(
                email="ADeCurtis123@gmail.com",
                password=password,
                username="Antonio de Curtis",
                name="Antonio",
                surname="De Curtis",
                token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe5196"
                      "91a7ad17643eecbe13d1c8c4adccd2",
                isResearcher=False,
                key=Fernet.generate_key()
            )
            db.session.add(utente)
            db.session.commit()

    def teardown_method(self):
        self.driver.quit()
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@127.0.0.1/quantumknn_db"
        if database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            with app.app_context():
                db.session.delete(User.query.filter_by(email="ADeCurtis123@gmail.com").first())
                db.session.commit()

    def test_user_not_registered(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1936, 1048)
        self.driver.find_element(By.CSS_SELECTOR, ".user").click()
        self.driver.find_element(By.ID, "login").send_keys("ADeCurtis123gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Password123")
        self.driver.find_element(By.CSS_SELECTOR, ".fourth").click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p#errore'))
        )
        msg_content = self.driver.find_element(By.CSS_SELECTOR, "p#errore").text

        assert "Utente non registrato" == msg_content


    def test_invalid_password(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1936, 1048)
        self.driver.find_element(By.CSS_SELECTOR, ".user").click()
        self.driver.find_element(By.ID, "login").send_keys("ADeCurtis123@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Pass")
        self.driver.find_element(By.CSS_SELECTOR, ".fourth").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p#errore'))
        )
        msg_content = self.driver.find_element(By.CSS_SELECTOR, "p#errore").text

        assert "password errata" == msg_content
    def test_success(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1936, 1048)
        self.driver.find_element(By.CSS_SELECTOR, ".user").click()
        self.driver.find_element(By.ID, "login").send_keys("ADeCurtis123@gmail.com")
        self.driver.find_element(By.ID, "password").send_keys("Password123")
        self.driver.find_element(By.CSS_SELECTOR, ".fourth").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'label#username'))
        )
        msg_content = self.driver.find_element(By.CSS_SELECTOR, "label#username").text

        assert "Antonio de Curtis" == msg_content
