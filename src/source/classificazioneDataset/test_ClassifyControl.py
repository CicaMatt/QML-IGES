import hashlib
import os
import pathlib
import time
import unittest
from datetime import datetime
from os.path import exists
from cryptography.fernet import Fernet
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy_utils import database_exists, create_database, drop_database
from src import db
import flask
from src import app
from src.source.classificazioneDataset.ClassifyControl import ClassificazioneControl
from src.source.model.models import User, Dataset
from src.source.utils import utils


class TestClassifyControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "mysql://root@127.0.0.1/test_db"
        if database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            with app.app_context():
                drop_database(app.config["SQLALCHEMY_DATABASE_URI"])
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        create_database(app.config["SQLALCHEMY_DATABASE_URI"])
        with app.app_context():
            db.create_all()
            password = "quercia1234"
            password = hashlib.sha512(password.encode()).hexdigest()
            utente = User(
                email="boscoverde27@gmail.com",
                password=password,
                username="Antonio de Curtis",
                name="Antonio",
                surname="De Curtis",
                token="43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe5196" \
                      "91a7ad17643eecbe13d1c8c4adccd2",
                isResearcher=False,
                key=Fernet.generate_key()
            )
            salvataggiodatabase = Dataset(
                email_user="boscoverde27@gmail.com",
                name="bupa.csv",
                upload_date=datetime.now(),
                validation="Simple Split",
                ps=False,
                fs=False,
                fe=False,
                model="Random Forest Classifier",
            )
            db.session.add(utente)
            db.session.commit()
            db.session.add(salvataggiodatabase)
            db.session.commit()

            path = pathlib.Path.home() / "QMLdata" / "boscoverde27@gmail.com"
            if not path.is_dir():
                path.mkdir()
            path_exp = path / "1"
            if not path_exp.is_dir():
                path_exp.mkdir()

            if os.path.exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "classifiedFile.csv"
            ):
                os.remove(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "classifiedFile.csv"
                )
            open(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "emptyFile.csv",
                "w",
            ).write("1234567890987654321")


    def test_classify_control(self):
        """
        Test the input coming from the form and the status code returned, and check if the classification result
        file is created
        """
        tester = app.test_client(self)
        with tester:
            response = tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia1234"),
            )

            path_train = (
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "DataSetTrainPreprocessato.csv"
            )
            path_test = (
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "DataSetTestPreprocessato.csv"
            )
            path_prediction = (
                pathlib.Path(__file__).resolve().parent / "testingFiles" / "doPrediction.csv"
            )
            print(path_train, path_test, path_prediction)
            features = utils.createFeatureList(2)
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe5196" \
                    "91a7ad17643eecbe13d1c8c4adccd2"
            backend = "aer_simulator"
            email = "boscoverde27@gmail.com"
            model = "SVC"
            C = 2
            tau = 2
            optimizer = "ADAM"
            loss = "squared_error"
            max_iter = 10
            kernelSVR = "rbf"
            kernelSVC = "rbf"
            C_SVC = 1
            C_SVR = 1
            id_dataset = str(Dataset.query.filter_by(
                email_user=current_user.email).order_by(
                desc(
                    Dataset.id)).first().id)

            response = app.test_client(self).post(
                "/classify_control",
                data=dict(
                    pathTrain=path_train,
                    pathTest=path_test,
                    email=email,
                    userpathToPredict=path_prediction,
                    features=features,
                    token=token,
                    backend=backend,
                    model=model,
                    C=C,
                    tau=tau,
                    optimizer=optimizer,
                    loss=loss,
                    max_iter=max_iter,
                    kernelSVR=kernelSVR,
                    kernelSVC=kernelSVC,
                    C_SVC=C_SVC,
                    C_SVR=C_SVR,
                    id_dataset=id_dataset
                ),
            )
            thread = flask.g
            thread.join()
            statuscode = response.status_code
            self.assertEqual(200, statuscode)

    def test_classification_thread(self):
        """
        Test if thread that calls the classify and QSVM works properly
        """

        tester = app.test_client(self)
        with tester:
            response = tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia1234"),
            )

            path_train = (
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "DataSetTrainPreprocessato.csv"
            )
            path_test = (
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "DataSetTestPreprocessato.csv"
            )
            path_prediction = (
                    pathlib.Path(__file__).resolve().parent / "testingFiles" / "doPrediction.csv"
            )
            features = utils.createFeatureList(2)
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe5196" \
                    "91a7ad17643eecbe13d1c8c4adccd2"
            backend_selected = "aer_simulator"
            email = "boscoverde27@gmail.com"
            model = "Random Forest Classifier"
            C = 2
            tau = 2
            optimizer = "ADAM"
            loss = "squared_error"
            max_iter = 10
            kernelSVR = "rbf"
            kernelSVC = "rbf"
            C_SVC = 1
            C_SVR = 1
            id_dataset = str(Dataset.query.filter_by(
                email_user=current_user.email).order_by(
                desc(
                    Dataset.id)).first().id)

            result = ClassificazioneControl().classification_thread(path_train, path_test, path_prediction, features,
                                                                    token, backend_selected, email, model, C, tau,
                                                                    optimizer, loss, max_iter, kernelSVR, kernelSVC,
                                                                    C_SVC, C_SVR, id_dataset)

            self.assertNotEqual(result["error"], 1)
            self.assertTrue(
                exists(
                    pathlib.Path().home() / "QMLdata" / email / id_dataset / "classifiedFile.dat"
                )
            )
            self.assertTrue(
                exists(
                    pathlib.Path().home() / "QMLdata" / email / id_dataset / "model.dat"
                )
            )

    def test_classify(self):
        """
        Test the classify function with correct parameters and input files, and check if the classification result
        file is created
        """

        tester = app.test_client(self)
        with tester:
            response = tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia1234"),
            )

            path_train = (
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "DataSetTrainPreprocessato.csv"
            )
            path_test = (
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "DataSetTestPreprocessato.csv"
            )
            path_prediction = (
                pathlib.Path(__file__).resolve().parent / "testingFiles" / "doPrediction.csv"
            )
            features = utils.createFeatureList(2)
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519" \
                    "691a7ad17643eecbe13d1c8c4adccd2"
            backend_selected = "aer_simulator"
            model = "Random Forest Classifier"
            C = 2
            tau = 2
            optimizer = "ADAM"
            loss = "squared_error"
            max_iter = 10
            kernelSVR = "rbf"
            kernelSVC = "rbf"
            C_SVC = 1
            C_SVR = 1
            id_dataset = str(Dataset.query.filter_by(
                email_user=current_user.email).order_by(
                desc(
                    Dataset.id)).first().id)

            result = ClassificazioneControl().classify(path_train, path_test, path_prediction, features,
                                                       token, backend_selected, model, C, tau,
                                                       optimizer, loss, max_iter, kernelSVR, kernelSVC,
                                                       C_SVC, C_SVR, id_dataset, current_user.email
                                                       )

            self.assertNotEqual(result["error"], 1)
            self.assertTrue(
                exists(
                    pathlib.Path().home() / "QMLdata" / current_user.email / id_dataset / "classifiedFile.csv"
                )
            )
            self.assertTrue(
                exists(
                    pathlib.Path().home() / "QMLdata" / current_user.email / id_dataset / "model.sav"
                )
            )

    def test_getClassifiedDataset(self):
        """
        Test the function that send the email, with fixed parameters as input
        """
        result = {
            "testing_accuracy": 0.55687446747,
            "testing_precision": 0.55687446747,
            "testing_recall": 0.55687446747,
            "f1": 0.55687446747,
            "training_time": str(0.23434354),
            "test_success_ratio": 0.4765984595,
            "total_time": str(90.7),
            "error": 0,
            "no_backend": True,
            "model": "QSVC"
        }

        path = pathlib.Path.home() / "QMLdata" / "boscoverde27@gmail.com"
        if not path.is_dir():
            path.mkdir()
        path_exp = path / "1"
        if not path_exp.is_dir():
            path_exp.mkdir()
        open(
            path_exp / "classifiedFile.csv",
            "w",
        ).write("test")

        value = ClassificazioneControl().get_classified_dataset(
            result, "boscoverde27@gmail.com", "Random Forest Classifier", "simulator", "1"
        )
        self.assertEqual(value, 1)

    def test_classify_ibmFail(self):
        """
        Test the classify function with not valid train and test datasets, to make the IBM backend fail on purpose
        """
        tester = app.test_client(self)
        with tester:
            response = tester.post(
                "/login",
                data=dict(email="boscoverde27@gmail.com", password="quercia1234"),
            )
            path_train = (
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "DataSetTrainPreprocessato.csv"
            )
            path_test = (
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "DataSetTestPreprocessato.csv"
            )
            path_prediction = (
                    pathlib.Path(__file__).resolve().parent / "testingFiles" / "emptyFile.csv"
            )
            features = utils.createFeatureList(2)
            token = "43a75c20e78cef978267a3bdcdb0207dab62575c3c9da494a1cd344022abc8a326ca1a9b7ee3f533bb7ead73a5f9fe519691" \
                    "a7ad17643eecbe13d1c8c4adccd2"
            backend_selected = "aer_simulator"
            model = "SVC"
            C = 2
            tau = 2
            optimizer = "ADAM"
            loss = "squared_error"
            max_iter = 10
            kernelSVR = "rbf"
            kernelSVC = "rbf"
            C_SVC = 1
            C_SVR = 1
            id_dataset = str(Dataset.query.filter_by(
                email_user=current_user.email).order_by(
                desc(
                    Dataset.id)).first().id)

            path = pathlib.Path.home() / "QMLdata" / current_user.email
            path_exp = path / "1"
            if not path.is_dir():
                path.mkdir()
            if not path_exp.is_dir():
                path_exp.mkdir()

            result = ClassificazioneControl().classify(path_train, path_test, path_prediction, features,
                                                       token, backend_selected, model, C, tau,
                                                       optimizer, loss, max_iter, kernelSVR, kernelSVC,
                                                       C_SVC, C_SVR, id_dataset, current_user.email
                                                       )
            self.assertEqual(result["error"], 1)
            self.assertFalse(
                exists(
                    pathlib.Path.home() / "QMLdata" / current_user.email / "1"
                    / "classifiedFile.dat"
                )
            )
            self.assertFalse(
                exists(
                    pathlib.Path.home() / "QMLdata" / current_user.email / "1"
                    / "model.dat"
                )
            )

    def tearDown(self):
        if os.path.exists(
            pathlib.Path().home() / "QMLdata" / "boscoverde27@gmail.com" / "1" / "classifiedFile.dat"
        ):
            os.remove(
                pathlib.Path().home() / "QMLdata" / "boscoverde27@gmail.com" / "1"
                / "classifiedFile.dat"
            )

        if os.path.exists(
                pathlib.Path().home() / "QMLdata" / "boscoverde27@gmail.com" / "1"
                / "model.dat"
        ):
            os.remove(
                pathlib.Path().home() / "QMLdata" / "boscoverde27@gmail.com" / "1"
                / "model.dat"
            )

        ###

        if os.path.exists(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "classifiedFile.dat"
        ):
            os.remove(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "classifiedFile.dat"
            )
        if os.path.exists(
            pathlib.Path(__file__).resolve().parent
            / "testingFiles"
            / "model.dat"
        ):
            os.remove(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "model.dat"
            )
        if os.path.exists(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "emptyFile.dat"
        ):
            os.remove(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "emptyFile.dat"
            )

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.close_all()
            db.drop_all()
