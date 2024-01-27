# Generated by Selenium IDE
import hashlib
import pathlib

from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC

import pytest
import time
import json

from cryptography.fernet import Fernet
from flask_login import current_user
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sqlalchemy import desc
from sqlalchemy_utils import database_exists, create_database, drop_database

from src import app, db
from src.source.model.models import User, Dataset


class TestDataset():
  def setup_method(self):
    self.driver = webdriver.Chrome()
    self.vars = {}
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@127.0.0.1/quantumknn_db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
      self.driver.get("http://127.0.0.1:5000/")
      self.driver.set_window_size(1936, 1048)
      self.driver.find_element(By.LINK_TEXT, "QUANTUM ML").click()
      self.driver.find_element(By.ID, "login").send_keys("ADeCurtis123@gmail.com")
      self.driver.find_element(By.ID, "password").send_keys("Password123")
      self.driver.find_element(By.CSS_SELECTOR, ".fourth").click()
      self.driver.find_element(By.LINK_TEXT, "QUANTUM ML").click()
  
  def teardown_method(self):
    self.driver.quit()
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@127.0.0.1/quantumknn_db"
    if database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
      with app.app_context():
        result = Dataset.query.filter_by(email_user="ADeCurtis123@gmail.com").order_by(desc(Dataset.id)).first()
        if result is not None:
          db.session.delete(result)
          db.session.commit()
        db.session.delete(User.query.filter_by(email="ADeCurtis123@gmail.com").first())
        db.session.commit()
  
  def test_form_success_train_pred(self):
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupaToPredict.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    assert self.driver.current_url == "http://127.0.0.1:5000/formcontrol"

  def test_form_success_train_test_pred(self):
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupaToPredict.csv"))
    self.driver.find_element(By.ID, "inputFileTest").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupaTest.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    assert self.driver.current_url == "http://127.0.0.1:5000/formcontrol"

  def test_form_success_only_train(self):
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    assert self.driver.current_url == "http://127.0.0.1:5000/formcontrol"

  def test_form_empty_train(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "emptyFile.csv",
      "w",
    ).write("")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(str(path / "emptyFile.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupaToPredict.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'p#errore'))
    )
    msg_content = self.driver.find_element(By.CSS_SELECTOR, "p#errore").text

    assert "Empty dataset inserted" == msg_content

  def test_form_empty_prediction(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "emptyFile.csv",
      "w",
    ).write("")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(str(path / "emptyFile.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'p#errore'))
    )
    msg_content = self.driver.find_element(By.CSS_SELECTOR, "p#errore").text

    assert "Empty dataset inserted" == msg_content

  def test_form_empty_test(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "emptyFile.csv",
      "w",
    ).write("")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupaToPredict.csv"))
    self.driver.find_element(By.ID, "inputFileTest").send_keys(str(path / "emptyFile.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'p#errore'))
    )
    msg_content = self.driver.find_element(By.CSS_SELECTOR, "p#errore").text

    assert "Empty dataset inserted" == msg_content

  def test_form_empty_test(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "emptyFile.csv",
      "w",
    ).write("")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupaToPredict.csv"))
    self.driver.find_element(By.ID, "inputFileTest").send_keys(str(path / "emptyFile.csv"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, 'p#errore'))
    )
    msg_content = self.driver.find_element(By.CSS_SELECTOR, "p#errore").text

    assert "Empty dataset inserted" == msg_content

  def test_train_bad_format(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "test.txt",
      "w",
    ).write("12345")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "test.txt"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    alert = Alert(self.driver)

    assert "Training set non inserito e/o non valido" == alert.text

  def test_test_bad_format(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "test.txt",
      "w",
    ).write("12345")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFileTest").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "test.txt"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    alert = Alert(self.driver)

    assert "Test set non valido" == alert.text

  def test_prediction_bad_format(self):
    path = pathlib.Path(__file__).resolve().parent.parent / "testingFiles"
    open(
      path
      / "test.txt",
      "w",
    ).write("12345")
    self.driver.find_element(By.ID, "inputFileTrain").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "bupa.csv"))
    self.driver.find_element(By.ID, "inputFilePrediction").send_keys(
      str(pathlib.Path(__file__).resolve().parent.parent / "testingFiles" / "test.txt"))
    element = self.driver.find_element(By.ID, "submitForm")
    self.driver.execute_script("arguments[0].click();", element)
    alert = Alert(self.driver)

    assert "Prediction test non valido" == alert.text