import hashlib
import os
import pathlib
import unittest
from datetime import datetime
from os.path import exists
from cryptography.fernet import Fernet
from flask_login import current_user
from sqlalchemy import desc
from sqlalchemy_utils import database_exists, create_database
from src import db
import flask
from src import app
from src.source.classificazioneDataset.ClassifyControl import ClassificazioneControl
from src.source.model.models import User, Dataset
from src.source.utils import utils


class TestClassifyControl(unittest.TestCase):
    def setUp(self):
        super().setUp()
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "mysql://root@127.0.0.1/test_db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        with app.app_context():
            db.drop_all()
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
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
            email = "quantumoonlight@gmail.com"
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
            user_id = current_user.email

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
                    id_dataset=id_dataset,
                    User=user_id
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
            email = "quantumoonlight@gmail.com"
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
            user_id = current_user.email

            result = ClassificazioneControl().classification_thread(path_train, path_test, path_prediction, features,
                                                                    token, backend_selected, email, model, C, tau,
                                                                    optimizer, loss, max_iter, kernelSVR, kernelSVC,
                                                                    C_SVC, C_SVR, id_dataset, user_id)

            self.assertNotEqual(result["error"], 1)
            self.assertTrue(
                exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "classifiedFile.csv"
                )
            )
            self.assertTrue(
                exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "model.sav"
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
            user_id = current_user.email

            result = ClassificazioneControl().classify(path_train, path_test, path_prediction, features,
                                                                    token, backend_selected, model, C, tau,
                                                                    optimizer, loss, max_iter, kernelSVR, kernelSVC,
                                                                    C_SVC, C_SVR, id_dataset, user_id
            )

            self.assertNotEqual(result["error"], 1)
            self.assertTrue(
                exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "classifiedFile.csv"
                )
            )
            self.assertTrue(
                exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "model.sav"
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
        open(
            pathlib.Path(__file__).resolve().parent
            / "testingFiles"
            / "classifiedFile.csv",
            "w",
        )
        user_path_to_predict = (
            pathlib.Path(__file__).resolve().parent / "testingFiles" / "doPrediction.csv"
        )

        value = ClassificazioneControl().get_classified_dataset(
            result, user_path_to_predict, "quantumoonlight@gmail.com", "Random Forest Classifier", "simulator"
        )
        self.assertEqual(value, 1)

    def tearDown(self):
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

        if os.path.exists(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "model.sav"
        ):
            os.remove(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "model.sav"
            )

        with app.app_context():
            db.drop_all()

class TestIbmFail(unittest.TestCase):

    def setUp(self):

        super().setUp()
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "mysql://root@127.0.0.1/test_db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        with app.app_context():
            db.drop_all()
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
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
            user_id = current_user.email

            result = ClassificazioneControl().classify(path_train, path_test, path_prediction, features,
                                                       token, backend_selected, model, C, tau,
                                                       optimizer, loss, max_iter, kernelSVR, kernelSVC,
                                                       C_SVC, C_SVR, id_dataset, user_id
                                                       )
            self.assertEqual(result["error"], 1)
            self.assertFalse(
                exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "classifiedFile.csv"
                )
            )
            self.assertFalse(
                exists(
                    pathlib.Path(__file__).resolve().parent
                    / "testingFiles"
                    / "model.sav"
                )
            )

    def tearDown(self) -> None:
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
        if os.path.exists(
            pathlib.Path(__file__).resolve().parent
            / "testingFiles"
            / "model.sav"
        ):
            os.remove(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "model.sav"
            )
        if os.path.exists(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "emptyFile.csv"
        ):
            os.remove(
                pathlib.Path(__file__).resolve().parent
                / "testingFiles"
                / "emptyFile.csv"
            )
