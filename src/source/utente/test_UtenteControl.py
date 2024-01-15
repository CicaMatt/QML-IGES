import hashlib
import os
import shutil
import time
from unittest.mock import patch
from zipfile import ZipFile
from pathlib import Path
from unittest import TestCase

from cryptography.fernet import Fernet
from flask_login import current_user, UserMixin, AnonymousUserMixin
from sqlalchemy_utils import database_exists, create_database, drop_database

from src import app, db
from src.source.model.models import User
from src.source.utente.UtenteControl import UtenteControl
from src.source.utils.encryption import encrypt


class Test_signup(TestCase):
    def setUp(self):
        super().setUp()
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "mysql://root@127.0.0.1/test_db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        with app.app_context():
            db.create_all()
            user = User(
                email="mariorossi@gmail.com",
                password="prosopagnosia",
                username="MarioRoss",
                name="Mario",
                surname="Rossi",
                token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2"
            )
            db.session.add(user)
            db.session.commit()

    def test_signup(self):
        """
        test the sign-up functionality of the website, creating a dummy  account and verifying it was correctly
        registered as a user
        """
        tester = app.test_client()
        with tester:
            response = tester.post(
                "/signup",
                data=dict(
                    email="mariorossi12@gmail.com",
                    password="Password123",
                    confirmPassword="Password123",
                    username="Antonio de Curtis ",
                    token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691a7ad17643eecbe13d1c8c4adccd2",
                    nome="Antonio",
                    cognome="De Curtis",
                ),
            )
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertTrue(
                User.query.filter_by(email="mariorossi12@gmail.com").first()
            )
            db.session.commit()

    def test_signupInvalidToken(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty and verifying it was
        correctly registered as a user and the token was correctly parsed to Null
        """

        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="mariorossi12@gmail.com",
                password="Password123",
                confirmPassword="Password123",
                username="Antonio de Curtis ",
                token="0e906980a743e9313c848becb8810b2667535e188365e8db829e1c206421d1ec02360127de06b13013782ca87efc3b7487853aba99061df220b825adee92e316a57ef7a<f689eafea5",
                nome="Antonio",
                cognome="De Curtis",
            ),
        )
        print(response.get_data())
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user.token)
        db.session.commit()

    def test_signupInvalidUsername(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty username and verifying
        it wasn't correctly registered as a user
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123@gmail.com ",
                password="Password123",
                confirmPassword="Password123",
                nome="Antonio",
                cognome="De Curtis",
                token='0e906980a743e9313c848becb8810b2667535e188365e8db829e1c206421d1ec02360127de06b13013782ca87efc3b7487853aba99061df220b825adee92e316'
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_signupInvalidEmail(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty email and verifying it
        wasn't correctly registered as a user.
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123cfsdil.com ",
                password="Password123",
                confirmPassword="Password123",
                username="Antonio de Curtis ",
                nome="Antonio",
                cognome="De Curtis",
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_signupInvalidPassword(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty email and verifying it
        wasn't correctly registered as a user.
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123@gmail.com ",
                password="123456",
                confirmPassword="Password123",
                username="Antonio de Curtis ",
                nome="Antonio",
                cognome="De Curtis",
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_signupInvalidConfirmPassword(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty email and verifying it
        wasn't correctly registered as a user.
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123@gmail.com ",
                password="123456",
                confirmPassword="efkjhjefwikefji",
                username="Antonio de Curtis ",
                nome="Antonio",
                cognome="De Curtis",
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_signupInvalidName(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty username and verifying
        it wasn't correctly registered as a user
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123@gmail.com ",
                password="Password123",
                confirmPassword="Password123",
                nome="Antonio1",
                cognome="De Curtis",
                token='0e906980a743e9313c848becb8810b2667535e188365e8db829e1c206421d1ec02360127de06b13013782ca87efc3b7487853aba99061df220b825adee92e316'
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_signupInvalidSurName(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty username and verifying
        it wasn't correctly registered as a user
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123@gmail.com ",
                password="Password123",
                confirmPassword="Password123",
                nome="Mario",
                cognome="",
                token='0e906980a743e9313c848becb8810b2667535e188365e8db829e1c206421d1ec02360127de06b13013782ca87efc3b7487853aba99061df220b825adee92e316'
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_signupInvalidToken(self):
        """
        test the sign-up functionality of the website, creating a dummy  account with an empty username and verifying
        it wasn't correctly registered as a user
        """
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        tester = app.test_client()
        response = tester.post(
            "/signup",
            data=dict(
                email="ADeCurtis123@gmail.com ",
                password="Password123",
                confirmPassword="Password123",
                nome="",
                cognome="De Curtis",
                token='0e906980a743e9313c848becb8810b2667535e188365e8db829e1c206421d1ec02360127de06b13013782ca87efc3b7487853aba99061df220b825adee92e316a57ef7a<f689eafea5 '
            ),
        )
        user = User.query.filter_by(email="mariorossi12@gmail.com").first()
        self.assertIsNone(user)
        db.session.commit()

    def test_SetNewPW(self):
        """
        test the sendCode functionality, checking first that the account exists,
        then modify it and verify that it has been modified correctly
        """
        tester = app.test_client()
        with tester:
            response = tester.post(
                "/SetNewPW",
                data=dict(
                    email="mariorossi@gmail.com",
                    pw="qwertyqwerty",
                ),
            )
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_sendCode(self):
        """
        test the sendCode functionality, checking first that the account exists,
        then modify it and verify that it has been modified correctly
        """
        tester = app.test_client()
        with tester:
            response = tester.post(
                "/sendCode",
                data=dict(
                    email="mariorossi@gmail.com",
                ),
            )
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_sendCode_emailNotFoundError(self):
        """
        test the sendCode functionality, checking first that the account exists,
        then modify it and verify that it has been modified correctly
        """
        tester = app.test_client()
        with tester:
            response = tester.post(
                "/sendCode",
                data=dict(
                    email="inesistente@gmail.com",
                ),
            )
        statuscode = response.status_code
        self.assertEqual(statuscode, 400)

    @patch('src.source.utente.UtenteControl.UtenteControl.resetPW')
    def test_email_sending_failure(self, mock_send_email):
        mock_send_email.side_effect = Exception("Errore durante l'invio dell'email")

        with self.assertRaises(Exception):
            UtenteControl.resetPW()

    def tearDown(self):
        with app.app_context():
            db.session.close_all()
            db.drop_all()
        time.sleep(1)


class Test_Login_Logout(TestCase):
    def setUp(self):
        super().setUp()
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "mysql://root@127.0.0.1/test_db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        with app.app_context():
            db.create_all()
            password = "quercia"
            password = hashlib.sha512(password.encode()).hexdigest()
            utente = User(
                email="boscoverde27@gmail.com",
                password=password,
                username="Antonio de Curtis",
                name="Antonio",
                surname="De Curtis",
                token="",
                isResearcher=False,
                key=Fernet.generate_key()
            )
            db.session.add(utente)
            db.session.commit()

    def test_LoginLogout(self):
        """
        test the login functionality of the website,by trying to log in a predetermined and existing user account and
        then logging out
        """
        tester = app.test_client()
        self.assertFalse(current_user)
        with tester:
            response = tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia"),
            )
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            assert isinstance(current_user, User)
            self.assertTrue(current_user.is_authenticated)
            response = tester.post("/logout")
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertFalse(current_user.is_authenticated)

    def test_loginUnregistered(self):
        tester = app.test_client()
        self.assertFalse(current_user)
        with tester:
            response = tester.post(
                "/login",
                data=dict(
                    email="emailsbagliata1234d@gmail.com",
                    password="quercia",
                ),
            )
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertNotIsInstance(current_user, UserMixin)
            self.assertIsInstance(current_user, AnonymousUserMixin)
            self.assertFalse(current_user.is_authenticated)

    def test_loginWrongPassword(self):
        tester = app.test_client()
        self.assertFalse(current_user)
        with tester:
            response = tester.post(
                "/login",
                data=dict(
                    email="boscoverde27@gmail.com",
                    password="passwordsbagliata",
                ),
            )
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertNotIsInstance(current_user, UserMixin)
            self.assertIsInstance(current_user, AnonymousUserMixin)
            self.assertFalse(current_user.is_authenticated)

    def test_Newsletter(self):
        tester = app.test_client()
        with tester:
            tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia"),
            )
            assert isinstance(current_user, User)
            self.assertFalse(current_user.newsletter)
            response = tester.post(
                "/newsletter",
                data=dict(email="boscoverde27@gmail.com"),
            )
            statuscode = response.status_code
            self.assertEqual(statuscode, 200)
            self.assertTrue(current_user.newsletter)

    def test_Download(self):
        tester = app.test_client()
        with tester:
            tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia")
            )

            path = Path.home() / "QMLdata" / "boscoverde27@gmail.com" / "1"
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(path / "test.txt", 'w') as file:
                file.write("test")
            encrypt(path, current_user.key)

            response = tester.post(
                "/experimentDownload",
                data=dict(expID="1")
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual("application/x-zip-compressed", response.content_type)

            with open(path / 'zipfile.zip', 'wb') as file:
                file.write(response.data)

            with ZipFile(path / 'zipfile.zip', 'r') as zip_ref:
                self.assertIsNone(zip_ref.testzip())

    def test_Download_invalidPath(self):
        tester = app.test_client()
        with tester:
            tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia")
            )

            path = Path.home() / "QMLdata" / "boscoverde27@gmail.com" / "0"
            encrypt(path, current_user.key)

            response = tester.post(
                "/experimentDownload",
                data=dict(expID="0")
            )
            self.assertEqual(500, response.status_code)

    def tearDown(self):
        with app.app_context():
            db.drop_all()
            if os.path.exists(Path.home() / "QMLdata" / "boscoverde27@gmail.com"):
                shutil.rmtree(Path.home() / "QMLdata" / "boscoverde27@gmail.com")
