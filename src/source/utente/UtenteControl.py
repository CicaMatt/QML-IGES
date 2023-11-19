import hashlib
import itertools
import os
import pathlib
import random
import re
import shutil
import smtplib
import time
from datetime import timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import exists
from pathlib import Path
from threading import Thread
from zipfile import ZipFile

import flask
from cryptography.fernet import Fernet
from flask import request, render_template, flash, send_from_directory, jsonify, abort
from flask_login import login_user, logout_user, current_user

from src import app, db
from src.source.model.models import User
from src.source.utils.cleanZip import delete_zip
from src.source.utils.encryption import decrypt, encrypt


class UtenteControl:
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        """
                Reads the user credentials from a http request and adds him to the project database
                    :return: redirect to index page
                """
        email = request.form.get("email")
        password = request.form.get("password")
        cpassword = request.form.get("confirmPassword")
        hashed_password = hashlib.sha512(password.encode()).hexdigest()
        token = request.form.get("token")
        print(token)
        isResearcher = request.form.get("isResearcher")
        if token == "":
            token = None
        username = request.form.get("username")
        utente = User.query.filter_by(username=username).first()
        if utente:
            flash("Username is invalid or already taken", "error")
            return render_template("registration.html")
        Name = request.form.get("nome")
        cognome = request.form.get("cognome")
        if not 0 < username.__len__() < 30:
            flash(
                "Invalid username (length mus be between 1 and 30 characters)",
                "error")
            return render_template("registration.html")
        if not re.fullmatch(
                '^[A-z0-9._%+-]+@[A-z0-9.-]+\\.[A-z]{2,10}$',
                email):
            flash("Invalid email", "error")
            return render_template("registration.html")
        if not password.__len__() >= 8:
            flash("Password length has to be at least 8 characters", "error")
            return render_template("registration.html")
        if not password.__eq__(cpassword):
            flash("Password and confirm password do not match", "error")
            return render_template("registration.html")
        if not re.fullmatch('^[A-zÀ-ù ‘-]{2,30}$', Name):
            flash(
                "Invalid name, ,name must contain only alphabetical characters",
                "error")
            return render_template("registration.html")
        if not re.fullmatch('^[A-zÀ-ù ‘-]{2,30}$', cognome):
            flash(
                "Invalid surname, ,surname must contain only alphabetical characters",
                "error")
            return render_template("registration.html")
        if not ((token is None) or token.__len__() == 128):
            flash("Invalid ibmq token", "error")
            return render_template("registration.html")

        utente = User.query.filter_by(email=email).first()
        if utente:
            flash("Email is invalid or already taken", "error")
            return render_template("registration.html")

        group = request.form.get("group")

        utente = User(
            email=email,
            password=hashed_password,
            token=token,
            username=username,
            name=Name,
            surname=cognome,
            isResearcher=bool(isResearcher),
            group=group,
            key=Fernet.generate_key()
        )

        db.session.add(utente)
        db.session.commit()

        path = Path.home() / "QMLdata" / email

        print(path.__str__())
        if not path.is_dir():
            path.mkdir()
        login_user(utente, duration=timedelta(days=365), force=True)
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        reads a user login credentials from a http request and if they are valid logs the user in with those same
        credentials,changing his state from anonymous  user to logged user
        :return: redirect to index page
        """
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hashlib.sha512(password.encode()).hexdigest()
        attempted_user: User = User.query.filter_by(email=email).first()
        if not attempted_user:
            print(attempted_user.__class__)
            flash("Utente non registrato", "error")
            return render_template("login.html")

        if attempted_user.password == hashed_password:
            login_user(attempted_user, duration=timedelta(days=365), force=True)
        else:
            flash("password errata", "error")
            return render_template("login.html")
        return render_template("index.html")

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        """
        logs a user out, changing his state from logged user to anonymous user
            :return:redirect to index page
        """
        logout_user()
        return render_template("index.html")

    @app.route("/SetNewPW", methods=["GET", "POST"])
    def SetNewPW():
        """
        logs a user out, changing his state from logged user to anonymous user
            :return:redirect to index page
        """
        password = request.form.get("pw")
        email = request.form.get("email")
        hashed_password = hashlib.sha512(password.encode()).hexdigest()
        utente = User.query.filter_by(email=email).first()
        if utente:
            utente.password = hashed_password
            db.session.commit()
        return render_template("index.html")

    @app.route("/sendCode", methods=["GET", "POST"])
    def resetPW():
        """
        send Verification Code
            :return: redirect to preview page
        """
        email = request.form.get('email')
        utente = User.query.filter_by(email=email).first()
        if utente is None:
            abort(400, "Error 400: Bad Request. No user found associated with the email")
        verification_code = str(random.randint(100000, 999999))

        msg = MIMEMultipart()
        msg["From"] = "quantumoonlight@gmail.com"
        msg["To"] = "lucacontrasto@gmail.com"
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = "Verification Code"

        msg.attach(
            MIMEText(
                '<td><center><img style="width:25%;" src="cid:image"></center></td>',
                'html'))
        img_path = open(
            pathlib.Path(__file__).resolve().parents[2] /
            "static" /
            "images" /
            "logos" /
            "Logo_SenzaScritta.png",
            "rb")
        img = MIMEImage(img_path.read())
        img.add_header('Content-ID', '<image>')
        msg.attach(img)
        msg.attach(
            MIMEText(
                "<center><h4>Verification Code:<t>" + verification_code, 'html'))
        try:
            recipients = ['quantumoonlight@gmail.com', email]
            session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
            session.ehlo()
            session.starttls()  # enable security
            session.login("quantumoonlight@gmail.com", "erkz pqec tbra duzo")  # login with mail_id and password
            session.sendmail("quantumoonlight@gmail.com", recipients, msg.__str__())
            session.quit()
        except BaseException as e:
            print(e.with_traceback())
            return abort(500, "Error 500:Internal Server Error. Cannot send email")
        return jsonify({'verification_code': verification_code})

    @app.route("/newsletter", methods=["GET", "POST"])
    def signup_newsletter():
        """
        changes the User ,whose email was passed as a http request parameter ,newsletter flag to true
            :return: redirect to index page
        """
        email = request.form.get("email")
        if re.fullmatch('^[A-z0-9._%+-]+@[A-z0-9.-]+\\.[A-z]{2,10}$', email):
            utente: User = User.query.filter_by(email=email).first()
            utente.newsletter = True
            db.session.commit()
            flash("Subscribed", "notifica")
            return render_template("index.html")
        else:
            flash("Invalid email format", "notifica")
            return render_template("index.html")

    @app.route("/download", methods=["GET", "POST"])
    def download():
        try:
            ID = request.form.get("id")
            filename = request.form.get("filename")
            filepath = Path.home() / "QMLdata" / current_user.email / ID

            if filename:
                # Quando l'applicazione sarà hostata su un web server sostituire
                # con un metodo di download fornito dal web server
                zip_name = ''
                if (filename == "Validation"):
                    zip_path = filepath / 'ValidationResult.zip'
                    zip_name = 'ValidationResult.zip'
                    zip = ZipFile(zip_path, 'w')
                    if exists(
                            filepath /
                            "Data_training.csv") and exists(
                        filepath /
                        "Data_testing.csv"):
                        zip.write(
                            filepath / "Data_training.csv",
                            "data_training.csv")
                        zip.write(
                            filepath / 'Data_testing.csv',
                            "data_testing.csv")

                    for count in itertools.count(start=1):
                        str_test = "testing_fold_" + count.__str__() + ".csv"
                        str_train = "training_fold_" + count.__str__() + ".csv"
                        if exists(filepath / str_test):
                            zip.write(filepath / str_test,
                                      str_test)
                            zip.write(filepath / str_train,
                                      str_train)
                        else:
                            break
                    zip.close()
                else:
                    zip_path = filepath / 'PreprocessingResult.zip'
                    zip_name = 'PreprocessingResult.zip'
                    zip = ZipFile(zip_path, 'w')
                    if exists(
                            filepath /
                            "DataSetTestPreprocessato.csv") and exists(
                        filepath /
                        "DataSetTrainPreprocessato.csv"):
                        zip.write(
                            filepath / 'DataSetTestPreprocessato.csv',
                            'DataSetTestPreprocessato.csv')
                        zip.write(
                            filepath / 'DataSetTrainPreprocessato.csv',
                            'DataSetTrainPreprocessato.csv')
                    if exists(filepath / "doPredictionFE.csv"):
                        zip.write(
                            filepath / 'doPredictionFE.csv',
                            'doPredictionFE.csv')
                    if exists(filepath / "reducedTrainingPS.csv"):
                        zip.write(
                            filepath / 'reducedTrainingPS.csv',
                            'reducedTrainingPS.csv')
                    if exists(
                            filepath /
                            "Test_Feature_Extraction.csv") and exists(
                        filepath /
                        "Train_Feature_Extraction.csv"):
                        zip.write(
                            filepath / 'Test_Feature_Extraction.csv',
                            'Test_Feature_Extraction.csv')
                        zip.write(
                            filepath / 'Train_Feature_Extraction.csv',
                            'Train_Feature_Extraction.csv')
                    if exists(filepath / "Train_Feature_Selection.csv"):
                        zip.write(
                            filepath / "Train_Feature_Selection.csv",
                            "Train_Feature_Selection.csv")
                    if exists(filepath / "Test_Feature_Selection.csv"):
                        zip.write(
                            filepath / "Test_Feature_Selection.csv",
                            "Test_Feature_Selection.csv")

                    if exists(filepath / "TrainImputation.csv"):
                        zip.write(
                            filepath / "TrainImputation.csv",
                            "TrainImputation.csv")
                    if exists(filepath / "TestImputation.csv"):
                        zip.write(
                            filepath / "TestImputation.csv",
                            "TestImputation.csv")
                    if exists(filepath / "PredictImputation.csv"):
                        zip.write(
                            filepath / "PredictImputation.csv",
                            "PredictImputation.csv")
                    if exists(filepath / "TrainScaled.csv"):
                        zip.write(filepath / "TrainScaled.csv", "TrainScaled.csv")
                    if exists(filepath / "TestScaled.csv"):
                        zip.write(filepath / "TestScaled.csv", "TestScaled.csv")
                    if exists(filepath / "PredictScaled.csv"):
                        zip.write(
                            filepath / "PredictScaled.csv",
                            "PredictScaled.csv")
                    zip.close()

                return send_from_directory(
                    directory=filepath,
                    path=zip_name
                )
            else:
                flash(
                    "Unable to download the file, try again",
                    "error")
                return render_template("downloadPage.html")
        finally:
            thread = Thread(target=delete_zip, args=(filepath,))
            thread.setDaemon(True)
            thread.start()

    @app.route("/experimentDownload", methods=["GET", "POST"])
    def experimentDownload():
        try:
            exp_id = request.form.get("expID")
            filepath = Path.home() / "QMLdata" / current_user.email / exp_id

            decrypt(filepath, current_user.key)

            zip_name = 'Experiment_' + str(exp_id) + '.zip'
            zip_file = ZipFile(filepath / zip_name, 'w')

            for root, dirs, files in os.walk(filepath):
                for file in files:
                    if os.path.splitext(file)[1] == ".dat" or os.path.splitext(file)[1] == ".zip":
                        continue
                    zip_file.write(filepath / file, file)
                    os.remove(filepath / file)

            zip_file.close()

            return send_from_directory(
                directory=filepath,
                path=zip_name
            )
        except:
            print("Error occurred during experiment download")
            flash("Unable to download the file, try again", "error")
        finally:
            thread = Thread(target=delete_zip, args=(filepath,))
            thread.setDaemon(True)
            thread.start()
